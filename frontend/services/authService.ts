import api from "@/lib/axios";
import type {
  LoginChallengeRequest,
  LoginChallengeResponse,
  LoginVerifyRequest,
  MeResponse,
  MessageResponse,
  RegisterRequest,
} from "@/lib/types/auth";

export const authService = {
  register: async (payload: RegisterRequest) => {
    const { data } = await api.post<MessageResponse>("/auth/register", payload);
    return data;
  },

  requestLoginChallenge: async (payload: LoginChallengeRequest) => {
    const { data } = await api.post<LoginChallengeResponse>(
      "/auth/login/challenge",
      payload,
    );
    return data;
  },

  verifyLoginProof: async (payload: LoginVerifyRequest) => {
    const { data } = await api.post<MessageResponse>("/auth/login/verify", payload);
    return data;
  },

  getCurrentUser: async () => {
    const { data } = await api.get<MeResponse>("/auth/me");
    return data;
  },

  logout: async () => {
    const { data } = await api.post<MessageResponse>("/auth/logout");
    return data;
  },
};
