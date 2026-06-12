import api from "./api";

export async function createShipment(shipmentData) {
  return api.post("/shipments", shipmentData);
}

export async function getShipmentByOrderId(orderId) {
  return api.get(`/shipments/order/${orderId}`);
}
