import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import Login from "../components/Login";

const renderLogin = () =>
  render(
    <BrowserRouter>
      <AuthProvider>
        <Login />
      </AuthProvider>
    </BrowserRouter>
  );

describe("Login Component", () => {
  it("should render login form with username and password fields", () => {
    renderLogin();
    expect(screen.getByLabelText(/usuario/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
  });

  it("should render submit button", () => {
    renderLogin();
    expect(screen.getByRole("button", { name: /iniciar sesión/i })).toBeInTheDocument();
  });

  it("should have register toggle link", () => {
    renderLogin();
    expect(screen.getByText(/registrarse/i)).toBeInTheDocument();
  });

  it("should render brand name", () => {
    renderLogin();
    expect(screen.getByText(/perfumer/i)).toBeInTheDocument();
  });

  it("should show register form when toggle is clicked", async () => {
    renderLogin();
    const toggle = screen.getByText(/registrarse/i);
    toggle.click();
    expect(await screen.findByRole("button", { name: /registrarse/i })).toBeInTheDocument();
  });
});
