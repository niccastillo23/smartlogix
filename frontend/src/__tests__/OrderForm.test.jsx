import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import OrderForm from "../components/OrderForm";

describe("OrderForm Component", () => {
  it("should render form title", () => {
    render(<OrderForm onSubmit={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.getByText(/detalles de envío/i)).toBeInTheDocument();
  });

  it("should render all form fields", () => {
    render(<OrderForm onSubmit={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.getByLabelText(/nombre completo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/dirección/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/ciudad/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/país/i)).toBeInTheDocument();
  });

  it("should render order type select", () => {
    render(<OrderForm onSubmit={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.getByLabelText(/tipo de pedido/i)).toBeInTheDocument();
  });

  it("should call onSubmit when form is submitted", async () => {
    const onSubmit = vi.fn();
    render(<OrderForm onSubmit={onSubmit} onCancel={vi.fn()} />);
    await userEvent.type(screen.getByLabelText(/nombre completo/i), "Juan Pérez");
    await userEvent.type(screen.getByLabelText(/email/i), "juan@test.com");
    await userEvent.type(screen.getByLabelText(/dirección/i), "Calle 123");
    await userEvent.type(screen.getByLabelText(/ciudad/i), "Santiago");
    await userEvent.type(screen.getByLabelText(/país/i), "Chile");
    await userEvent.click(screen.getByRole("button", { name: /confirmar pedido/i }));
    expect(onSubmit).toHaveBeenCalled();
  });

  it("should call onCancel when cancel button is clicked", async () => {
    const onCancel = vi.fn();
    render(<OrderForm onSubmit={vi.fn()} onCancel={onCancel} />);
    await userEvent.click(screen.getByRole("button", { name: /cancelar/i }));
    expect(onCancel).toHaveBeenCalled();
  });
});
