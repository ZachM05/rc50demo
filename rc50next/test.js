const now = new Date()
const alerts = {
    pressure: new Date(2022, 4, 1)
}

console.log((1/1000) * (now.getTime() - alerts.pressure.getTime()) > 60)