variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "insight-agent"
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "container_concurrency" {
  description = "Maximum number of concurrent requests per container"
  type        = number
  default     = 80
}

variable "min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "cpu" {
  description = "CPU allocation for each container"
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory allocation for each container"
  type        = string
  default     = "512Mi"
}

variable "ingress" {
  description = "Ingress settings for Cloud Run (internal, internal-and-cloud-load-balancing, all)"
  type        = string
  default     = "internal"

  validation {
    condition     = contains(["internal", "internal-and-cloud-load-balancing", "all"], var.ingress)
    error_message = "Ingress must be one of: internal, internal-and-cloud-load-balancing, all"
  }
}
