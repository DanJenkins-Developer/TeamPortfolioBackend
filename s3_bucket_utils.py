
from s3_bucket import s3_client
from fastapi import UploadFile


async def put_profile_picture(photo: UploadFile):

    content = await photo.read()
    s3_response = s3_client.put_object(
        Bucket='team-profile-pictures',
        Key=photo.filename,
        Body=content
    )
    photo_url = f"{'https://accesspoint1-dso6gt5myao37djcz38u3kksnyrbguse2a-s3alias.s3-accesspoint.us-east-2.amazonaws.com'}/{photo.filename}"

    return photo_url
