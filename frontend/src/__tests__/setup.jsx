import "@testing-library/jest-dom";
import { vi } from "vitest";

vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }) => {
      const { initial, animate, exit, whileHover, whileTap, whileInView, variants, custom, layout, viewport, transition, key, ...rest } = props;
      return <div {...rest} data-motion>{children}</div>;
    },
    span: ({ children, ...props }) => {
      const { initial, animate, exit, ...rest } = props;
      return <span {...rest} data-motion>{children}</span>;
    },
    p: ({ children, ...props }) => {
      const { initial, animate, exit, ...rest } = props;
      return <p {...rest} data-motion>{children}</p>;
    },
    h1: ({ children, ...props }) => {
      const { initial, animate, exit, transition, ...rest } = props;
      return <h1 {...rest} data-motion>{children}</h1>;
    },
    h2: ({ children, ...props }) => {
      const { initial, animate, exit, transition, ...rest } = props;
      return <h2 {...rest} data-motion>{children}</h2>;
    },
    section: ({ children, ...props }) => {
      const { initial, animate, transition, ...rest } = props;
      return <section {...rest} data-motion>{children}</section>;
    },
    header: ({ children, ...props }) => {
      const { initial, animate, transition, ...rest } = props;
      return <header {...rest} data-motion>{children}</header>;
    },
    aside: ({ children, ...props }) => {
      const { initial, animate, exit, transition, ...rest } = props;
      return <aside {...rest} data-motion>{children}</aside>;
    },
    img: ({ children, ...props }) => {
      const { key, ...rest } = props;
      return <img {...rest} data-motion />;
    },
    button: ({ children, ...props }) => {
      const { whileHover, whileTap, ...rest } = props;
      return <button {...rest} data-motion>{children}</button>;
    },
  },
  AnimatePresence: ({ children }) => <>{children}</>,
  LayoutGroup: ({ children }) => <>{children}</>,
}));
