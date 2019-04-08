import Map from "./Map";

window.onload = () => {
    const stateName = process.env.GATEWAY_HOST.split('.')[1]
    document.getElementById("state_name").textContent = stateName
    document.title = stateName
    Map();
}