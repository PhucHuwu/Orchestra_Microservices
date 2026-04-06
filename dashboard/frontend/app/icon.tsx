import type { ImageResponse } from "next/og";

export const size = {
  width: 32,
  height: 32
};

export const contentType = "image/png";

export default function Icon(): ImageResponse {
  return new Response(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
      <rect width="32" height="32" rx="8" fill="#0f766e"/>
      <circle cx="11" cy="16" r="3" fill="#ffffff"/>
      <circle cx="21" cy="16" r="3" fill="#ffffff"/>
      <rect x="10" y="9" width="2" height="14" fill="#ffffff"/>
      <rect x="20" y="9" width="2" height="14" fill="#ffffff"/>
      <path d="M12 10 C15 7,17 7,20 10" stroke="#ffffff" stroke-width="2" fill="none"/>
    </svg>`,
    {
      headers: {
        "Content-Type": "image/svg+xml"
      }
    }
  ) as unknown as ImageResponse;
}
