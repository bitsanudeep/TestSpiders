# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import functools
import hashlib
from cStringIO import StringIO

import logging
import psycopg2
import six
from PIL import Image
from scrapy.contrib.pipeline.images import ImageException, ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.settings import Settings
from scrapy.utils.misc import md5sum
from scrapy.utils.python import to_bytes
import imagehash,json,numpy as np

from scrapy.utils.request import referer_str
from scrapy.pipelines.files import FileException, FilesPipeline
from scrapy.exceptions import DropItem

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

logger = logging.getLogger(__name__)

class ImagesphashPipeline(ImagesPipeline):
    
    def get_media_requests(self, item, info):
        return [Request(x) for x in item.get('image_urls', [])]   
        
    def item_completed(self, results, item, info):
        item['images'] = [x for ok, x in results if ok]
        return item
    
    # Override the convert_image method to disable image conversion    
    def convert_image(self, image, size=None):
        buf = StringIO()        
        try:
            image.save(buf, image.format)
        except Exception, ex:
            raise ImageException("Cannot process image. Error: %s" % ex)

        return buf    
    
    def image_downloaded(self, response, request, info):
        checksum = None

        for width, height,url_sha2, phash_str, buf in self.get_images(response, request, info):
            if checksum is None:
                buf.seek(0)
                checksum = md5sum(buf)
            # self.store.persist_file(
            #     path, buf, info,
            #     meta={'width': width, 'height': height},
            #     headers={'Content-Type': 'image/jpeg'})
            
            #    hashString="".join([1 if x else 0 for x in hash])
        return width, height,url_sha2, phash_str,checksum

    def get_images(self, response, request, info):
        url_sha2 = self.file_sha2(request, response=response, info=info)
        orig_image = Image.open(BytesIO(response.body))
        phash = imagehash.phash(orig_image)
        phash_str = "".join(["1" if val else "0" for val in np.nditer(phash.hash, order='C') ])
        width, height = orig_image.size
        buf = self.convert_image(orig_image)
        yield width, height,url_sha2, phash_str, buf

    def file_sha2(self, request, response=None, info=None):
      
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest() 
        return image_guid

    
    def media_downloaded(self, response, request, info):
        referer = referer_str(request)

        if response.status != 200:
            logger.warning(
                'File (code: %(status)s): Error downloading file from '
                '%(request)s referred in <%(referer)s>',
                {'status': response.status,
                 'request': request, 'referer': referer},
                extra={'spider': info.spider}
            )
            raise FileException('download-error')

        if not response.body:
            logger.warning(
                'File (empty-content): Empty file from %(request)s referred '
                'in <%(referer)s>: no-content',
                {'request': request, 'referer': referer},
                extra={'spider': info.spider}
            )
            raise FileException('empty-content')

        status = 'cached' if 'cached' in response.flags else 'downloaded'
        logger.debug(
            'File (%(status)s): Downloaded file from %(request)s referred in '
            '<%(referer)s>',
            {'status': status, 'request': request, 'referer': referer},
            extra={'spider': info.spider}
        )
        self.inc_stats(info.spider, status)

        try:
            # path = self.file_path(request, response=response, info=info)
            width, height,url_sha2, phash,checksum = self.file_downloaded(response, request, info)
        except FileException as exc:
            logger.warning(
                'File (error): Error processing file from %(request)s '
                'referred in <%(referer)s>: %(errormsg)s',
                {'request': request, 'referer': referer, 'errormsg': str(exc)},
                extra={'spider': info.spider}, exc_info=True
            )
            raise
        except Exception as exc:
            logger.error(
                'File (unknown-error): Error processing file from %(request)s '
                'referred in <%(referer)s>',
                {'request': request, 'referer': referer},
                exc_info=True, extra={'spider': info.spider}
            )
            raise FileException(str(exc))
        resultDict = {'url': request.url, 'url_sha2': url_sha2, 'checksum': checksum, 'width':width, 'heigth':height, 'phash':phash}
        print json.dumps(resultDict)
        raise DropItem("Printed to console")

    # def image_key(self, url):
    #     image_guid = hashlib.sha1(url).hexdigest()
    #     return 'full/%s.jpg' % (image_guid)    
