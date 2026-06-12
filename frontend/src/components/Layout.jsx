import { Outlet } from "react-router-dom";
import Header from "./Header";
import CartDrawer from "./CartDrawer";

function Layout() {
  return (
    <div className="min-h-screen bg-cream-50 dark:bg-charcoal-900 transition-colors duration-300">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">
        <Outlet />
      </main>
      <CartDrawer />
    </div>
  );
}

export default Layout;
