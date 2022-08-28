import requests
from time import sleep
from datetime import datetime
from PIL import Image, ExifTags, TiffImagePlugin
import os
import hashlib
import json
from tqdm import tqdm

product_id = 1
count = 0
data = {}

try:
    while True:
        response = requests.get(f"https://api.digikala.com/v1/product/{str(product_id).zfill(7)}/comments/")
        status_code = response.status_code
        # if response.status_code == 200:
        response = response.json()["data"]["media_comments"]
        print(f" {product_id}[{str(status_code)}] - started at {datetime.now().strftime('%H:%M:%S')}")
        Sresponse = tqdm(total=len(response))
        for comment in response:
            try:
                data[response[count]["id"]] = {"product_id":product_id,"created_at":response[count]["created_at"],"user_name":response[count]["user_name"]}
                files = response[count]["files"]
                file_count = 0
                for file in files:
                    try:
                        url = files[file_count]["url"][0]
                        clear_url = str(url[:str(url).find('?')])
                        data[response[count]["id"]]["url"] = clear_url
                        with open("output.txt",'a') as output:
                            output.write(clear_url+"\n")
                        try:
                            with open(f'files/{clear_url[61:]}','wb') as file:
                                file.write(requests.get(clear_url).content)
                            img = Image.open(f'files/{clear_url[61:]}')
                            hash_image = hashlib.md5(img.tobytes()).hexdigest()
                            data[response[count]["id"]]["hash"] = hash_image
                            img_exif = img.getexif()
                            exif_list = {}
                            for key, val in img_exif.items():
                                    if key in ExifTags.TAGS:
                                        if isinstance(val, TiffImagePlugin.IFDRational):
                                            val = float(val)
                                        elif isinstance(val, tuple):
                                            val = tuple(float(t) if isinstance(t, TiffImagePlugin.IFDRational) else t for t in v)
                                        elif isinstance(val, bytes):
                                            val = val.decode(errors="replace")
                                        exif_list[ExifTags.TAGS[key]] = val
                                        # print(f'{ExifTags.TAGS[key]}: {val}')
                            data[response[count]["id"]]["exif"] = exif_list
                            os.remove(f'files/{clear_url[61:]}')
                            Sresponse.update(1)
                        except:
                            print("err")
                            pass
                        file_count += 1
                    except:
                        print("err2")
                        break
                count += 1
            except:
                print("err3")
                break
        with open("output.json","w") as output_json:
            json.dump(data, output_json, indent = 6)
        product_id += 1
        Sresponse.close()
except KeyboardInterrupt:
    with open("output.json","w") as output_json:
        json.dump(data, output_json, indent = 6)
