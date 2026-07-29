import type { ApplicationStatus } from "@/api/types";

export function statusTone(status: ApplicationStatus): "slate" | "green" | "amber" | "red" | "blue" {
  switch (status) {
    case "submitted":
      return "green";
    case "approved":
      return "blue";
    case "pending_approval":
      return "amber";
    case "rejected":
    case "failed":
      return "red";
    default:
      return "slate";
  }
}
