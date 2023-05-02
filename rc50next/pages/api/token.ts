import { WebPubSubServiceClient } from '@azure/web-pubsub';


async function getUrl() {
  let service = new WebPubSubServiceClient('Endpoint=https://rc50pub.webpubsub.azure.com;AccessKey=5ZjItb49u2WgWV/APoFeJ/wNdKwGnBKdHW79w5Cw8/Q=;Version=1.0;', 'rc50hub');
  let token = await service.getClientAccessToken({
    roles: ['webpubsub.joinLeaveGroup']
  });

  return token
}

const request = (req: any, res: any) =>
  new Promise(async (resolve, reject) => {
    try {
      const token = await getUrl()
      const body = JSON.stringify({ token: token })

      res.status(200).json(body);
      resolve(body);
    }
    catch (err) {
      console.log(err)
      res.status(404).json({ "status": "failed" });
      reject({ "status": "failed with error" });
    }
  });


export default request