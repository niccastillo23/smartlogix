// Pruebas de API contra el BFF (punto de entrada autenticado). Identificadores alineados con docs/pruebas.
import { test, expect } from "@playwright/test";

const usuario = () => `api${Date.now()}${Math.floor(Math.random() * 1000)}`;

let token;

test.beforeAll(async ({ request }) => {
  const r = await request.post("/api/auth/register", { data: { username: usuario(), password: "pass12345" } });
  expect(r.status()).toBe(200);
  token = (await r.json()).token;
});

test("API-01 endpoint protegido sin token responde 401", async ({ request }) => {
  const r = await request.get("/api/products");
  expect(r.status()).toBe(401);
});

test("API-02 listado de productos con token responde 200 con el catálogo", async ({ request }) => {
  const r = await request.get("/api/products", { headers: { Authorization: `Bearer ${token}` } });
  expect(r.status()).toBe(200);
  expect((await r.json()).length).toBeGreaterThanOrEqual(11);
});

test("API-03 tipo de orden no soportado responde 400 con mensaje controlado", async ({ request }) => {
  const r = await request.post("/api/orders", {
    headers: { Authorization: `Bearer ${token}` },
    data: { customerId: 1, customerName: "Test", email: "test@test.com", orderType: "INVALIDO",
            items: [{ productId: 1, productName: "Sauvage", quantity: 2, unitPrice: 100 }] },
  });
  expect(r.status()).toBe(400);
  expect((await r.json()).message).toContain("Tipo de orden no soportado");
});

test("API-04 actualizar estado de un pedido a través del BFF responde 200", async ({ request }) => {
  // Defecto INC-19 en la versión base: RestTemplate no soporta PATCH y el BFF responde 503.
  const crear = await request.post("/api/orders", {
    headers: { Authorization: `Bearer ${token}` },
    data: { customerId: 2, customerName: "Estado", email: "estado@test.com", orderType: "WEB",
            items: [{ productId: 1, productName: "Sauvage", quantity: 1, unitPrice: 100 }] },
  });
  expect(crear.status()).toBe(201);
  const id = (await crear.json()).id;
  const r = await request.patch(`/api/orders/${id}/status?status=SHIPPED`, { headers: { Authorization: `Bearer ${token}` } });
  expect(r.status()).toBe(200);
});

test("API-05 parámetro obligatorio ausente responde 400 y no 500", async ({ request }) => {
  // Defecto INC-20 en la versión base: MissingServletRequestParameterException devuelve 500.
  const r = await request.get("/api/products/price-range?max=150", { headers: { Authorization: `Bearer ${token}` } });
  expect(r.status()).toBe(400);
});

test("API-06 con token inválido se rechaza el acceso", async ({ request }) => {
  const r = await request.get("/api/products", { headers: { Authorization: "Bearer token.invalido.firma" } });
  expect(r.status()).toBe(401);
});
