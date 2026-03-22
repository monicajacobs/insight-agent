terraform {
  required_version = ">= 1.14.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "pawaitassessment-terraform-state"
    prefix = "insight-agent/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
