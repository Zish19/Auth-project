export interface RegisterRequest {
  username: string;
  public_key: string;
}

export interface LoginChallengeRequest {
  username: string;
}

export interface LoginChallengeResponse {
  challenge_id: string;
  challenge: string;
  expires_in: number;
}

export interface LoginVerifyRequest {
  username: string;
  challenge_id: string;
  R: string;
  s: string;
}

export interface MessageResponse {
  message: string;
}

export interface MeResponse {
  username: string;
}

export interface SessionMeta {
  fetchedAt: string;
  status: "authenticated" | "loading" | "error";
}
