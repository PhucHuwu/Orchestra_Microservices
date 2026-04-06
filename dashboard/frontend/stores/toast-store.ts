import { create } from "zustand";

export type ToastType = "success" | "error" | "info";

export type ToastItem = {
  id: string;
  title: string;
  description?: string;
  type: ToastType;
};

type ToastState = {
  items: ToastItem[];
  push: (toast: Omit<ToastItem, "id">) => void;
  remove: (id: string) => void;
};

export const useToastStore = create<ToastState>((set, get) => ({
  items: [],
  push: (toast) => {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    set({ items: [...get().items, { ...toast, id }] });

    setTimeout(() => {
      get().remove(id);
    }, 3500);
  },
  remove: (id) => set({ items: get().items.filter((item) => item.id !== id) })
}));
