terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
resource "aws_vpc" "autosre_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "AutoSRE-VPC"
    Environment = var.environment
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id            = aws_vpc.autosre_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "AutoSRE-Public-Subnet"
    Environment = var.environment
  }
}

resource "aws_subnet" "private_subnet" {
  vpc_id            = aws_vpc.autosre_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "AutoSRE-Private-Subnet"
    Environment = var.environment
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "autosre_cluster" {
  name = "autosre-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "AutoSRE-ECS-Cluster"
    Environment = var.environment
  }
}

# Application Load Balancer
resource "aws_lb" "autosre_alb" {
  name               = "autosre-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_subnet.id]

  tags = {
    Name = "AutoSRE-ALB"
    Environment = var.environment
  }
}

# Security Groups
resource "aws_security_group" "alb_sg" {
  name        = "autosre-alb-sg"
  description = "Security group for AutoSRE ALB"
  vpc_id      = aws_vpc.autosre_vpc.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "AutoSRE-ALB-SG"
    Environment = var.environment
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "autosre_logs" {
  name              = "/ecs/autosre"
  retention_in_days = 30

  tags = {
    Name = "AutoSRE-Logs"
    Environment = var.environment
  }
} 