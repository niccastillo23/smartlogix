// Flujos de usuario en el navegador. Identificadores alineados con docs/pruebas (UI-01 a UI-05).
import { test, expect } from "@playwright/test";

const usuario = () => `e2e${Date.now()}${Math.floor(Math.random() * 1000)}`;
const clave = "pass12345";

async function registrar(page, user) {
  await page.goto("/login");
  await page.getByRole("button", { name: "Registrarse" }).last().click();
  await page.fill("#username", user);
  await page.fill("#password", clave);
  await page.locator("button[type=submit]").click();
  await expect(page.getByText("Registro exitoso")).toBeVisible();
}

test("UI-01 acceso a una ruta protegida sin sesión redirige a login", async ({ page }) => {
  await page.goto("/catalog");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.locator("#username")).toBeVisible();
});

test("UI-02 registro de un usuario nuevo muestra confirmación", async ({ page }) => {
  await registrar(page, usuario());
});

test("UI-03 credenciales incorrectas muestran un mensaje de error", async ({ page }) => {
  const user = usuario();
  await registrar(page, user);
  await page.fill("#username", user);
  await page.fill("#password", "clave-incorrecta");
  await page.locator("button[type=submit]").click();
  // Comportamiento esperado: el formulario conserva los datos y muestra el error del BFF.
  // Defecto INC-18 en la versión base: el interceptor recarga la página y el error no se ve.
  await expect(page.getByText("Credenciales inválidas")).toBeVisible();
  await expect(page.locator("#username")).toHaveValue(user);
});

test("UI-04 inicio de sesión correcto lleva a la página principal", async ({ page }) => {
  const user = usuario();
  await registrar(page, user);
  await page.fill("#username", user);
  await page.fill("#password", clave);
  await page.locator("button[type=submit]").click();
  await expect(page).toHaveURL(/\/$/);
});

test("UI-05 el catálogo muestra los productos obtenidos del BFF", async ({ page }) => {
  const user = usuario();
  await registrar(page, user);
  await page.fill("#username", user);
  await page.fill("#password", clave);
  await page.locator("button[type=submit]").click();
  await expect(page).toHaveURL(/\/$/);
  await page.goto("/catalog");
  await expect(page.getByText("Nuestra Colección")).toBeVisible();
  await expect(page.getByText("Sauvage Eau de Parfum")).toBeVisible();
});
