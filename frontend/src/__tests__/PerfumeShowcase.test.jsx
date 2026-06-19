import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import PerfumeShowcase from "../components/ui/perfume-showcase";

describe("PerfumeShowcase Component", () => {
  it("should render without crashing", () => {
    const { container } = render(
      <MemoryRouter>
        <AuthProvider>
          <PerfumeShowcase />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(container.querySelector("main")).toBeTruthy();
  });

  it("should render the perfume title", () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <PerfumeShowcase />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(screen.getAllByText(/bleu de chanel/i).length).toBeGreaterThanOrEqual(1);
  });

  it("should render price", () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <PerfumeShowcase />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(screen.getAllByText(/\$[\d.]+/).length).toBeGreaterThanOrEqual(1);
  });

  it("should render switcher buttons", () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <PerfumeShowcase />
        </AuthProvider>
      </MemoryRouter>
    );
    const clasico = screen.getAllByText("Clásico");
    expect(clasico.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Dupe Árabe")).toBeInTheDocument();
  });

  it("should render link to catalog", () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <PerfumeShowcase />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(screen.getByText(/ver colección completa/i)).toBeInTheDocument();
  });
});
