
from s3_bucket import s3_client
from fastapi import UploadFile
import uuid
import os


async def put_profile_picture(photo: UploadFile):

    content = await photo.read()

    # to insure pictures aren't over written
    unique_filename = f"{uuid.uuid4()}-{photo.filename}"
    # unique_filename = f"ABSSFD{photo.filename}"
    # unique_filename = "ABSSFD" + photo.filename

    s3_response = s3_client.put_object(
        Bucket='team-profile-pictures',
        # Key=photo.filename,
        Key=unique_filename,
        Body=content
    )

    print(s3_response)
    # photo_url = f"{'https://accesspoint1-dso6gt5myao37djcz38u3kksnyrbguse2a-s3alias.s3-accesspoint.us-east-2.amazonaws.com'}/{unique_filename}"
    photo_url = unique_filename
    # photo_url = f"{'https://accesspoint1-dso6gt5myao37djcz38u3kksnyrbguse2a-s3alias.s3-accesspoint.us-east-2.amazonaws.com'}/{photo.filename}"

    return photo_url
