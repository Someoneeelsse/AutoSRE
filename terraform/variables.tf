variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "autosre"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "autosre.example.com"
} 