import { create } from "zustand";

type User = {
  id: string;
  email: string;
  full_name: string;
  role?: { name: string };
};

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  setSession: (accessToken: string, refreshToken: string, user?: User | null) => void;
  setUser: (user: User) => void;
  logout: () => void;
};

const storedAccess = localStorage.getItem("accessToken");
const storedRefresh = localStorage.getItem("refreshToken");

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: storedAccess,
  refreshToken: storedRefresh,
  user: null,
  setSession: (accessToken, refreshToken, user = null) => {
    localStorage.setItem("accessToken", accessToken);
    localStorage.setItem("refreshToken", refreshToken);
    set({ accessToken, refreshToken, user });
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    set({ accessToken: null, refreshToken: null, user: null });
  }
}));
