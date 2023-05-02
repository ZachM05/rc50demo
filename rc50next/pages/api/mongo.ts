import { RC50Data } from "../../src/types";
import mongoose, { ConnectOptions } from 'mongoose';

const { Schema } = mongoose;

// mongoose.connect(`mongodb://${process.env.NEXT_PUBLIC_DATABASE_HOST || '127.0.0.1'}/`, {
mongoose.connect(`mongodb://root:rootpassword@rc50db:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false`, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
    dbName: 'rc50data'
} as ConnectOptions);

export let RC50 = mongoose.models.RC50 || mongoose.model('RC50', new Schema({}, { strict: false }), 'rc50data');

export const find = async (): Promise<any> => {
    try {
        const data = await RC50.find().sort({ timestamp: -1 }).limit(300)
        return [data, null]
    } catch (err) {
        return [null, err]
    }
};

export const decrementLast = async () => {
    try {
        const doc = await RC50.find().sort({ timestamp: -1 }).limit(1)
        const update = { dispenseCount: 10000 };
        await doc[0].updateOne(update);
    } catch (err) {
        return { status: 'error', info: err }
    }
};



const request = (req: any, res: any) =>
    new Promise(async (resolve, reject) => {
        try {
            if (req.query) {
                await decrementLast();
            }

            const [data, err]: [RC50Data[], any] = await find()
            if (err) {
                console.log(err);
                res.status(404).json({ "status": "failed" });
                reject({ "status": "failed" });
            }
            const resultBody = JSON.stringify({
                data: data
            })
            res.status(200).json(resultBody);
            resolve(resultBody);

        } catch (error) {
            console.log(error);
            res.status(404).json({ "status": "failed" });
            reject({ "status": "failed with error" });
        }
    });

export default request;