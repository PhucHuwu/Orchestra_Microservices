import axios, { AxiosError } from "axios";
import { z } from "zod";

import { errorEnvelopeSchema, successEnvelopeSchema } from "./contracts";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiClientError extends Error {
  readonly code: string;
  readonly status?: number;

  constructor(message: string, code: string, status?: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

export const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 6000
});

function mapAxiosError(error: unknown): never {
  if (!(error instanceof AxiosError)) {
    throw new ApiClientError("Unexpected client error", "CLIENT_UNKNOWN");
  }

  if (error.code === "ECONNABORTED") {
    throw new ApiClientError("Request timeout", "CLIENT_TIMEOUT", error.response?.status);
  }

  if (!error.response) {
    throw new ApiClientError("Network unavailable", "CLIENT_NETWORK");
  }

  const parsed = errorEnvelopeSchema.safeParse(error.response.data);
  if (parsed.success) {
    throw new ApiClientError(parsed.data.message, parsed.data.error_code, error.response.status);
  }

  throw new ApiClientError("Backend error", "CLIENT_BACKEND", error.response.status);
}

export async function apiGet<T extends z.ZodTypeAny>(path: string, schema: T): Promise<z.infer<T>> {
  try {
    const response = await http.get(path);
    const parsed = successEnvelopeSchema(schema).safeParse(response.data);
    if (!parsed.success) {
      throw new ApiClientError("Invalid response envelope", "CLIENT_SCHEMA", response.status);
    }
    return parsed.data.data;
  } catch (error) {
    return mapAxiosError(error);
  }
}

export async function apiPost<T extends z.ZodTypeAny>(
  path: string,
  body: unknown,
  schema: T,
  options?: { timeoutMs?: number }
): Promise<z.infer<T>> {
  try {
    const response = await http.post(path, body, {
      timeout: options?.timeoutMs ?? http.defaults.timeout
    });
    const parsed = successEnvelopeSchema(schema).safeParse(response.data);
    if (!parsed.success) {
      throw new ApiClientError("Invalid response envelope", "CLIENT_SCHEMA", response.status);
    }
    return parsed.data.data;
  } catch (error) {
    return mapAxiosError(error);
  }
}
