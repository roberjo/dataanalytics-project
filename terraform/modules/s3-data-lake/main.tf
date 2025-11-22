# S3 Data Lake Module
# Creates S3 buckets for raw, processed, and curated data zones

resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project_name}-data-lake-${var.environment}"
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-data-lake-${var.environment}"
    Zone = "multi"
  })
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policies for cost optimization
resource "aws_s3_bucket_lifecycle_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  
  # Raw zone - transition to IA after 30 days, Glacier after 90 days
  rule {
    id     = "raw-zone-lifecycle"
    status = "Enabled"
    
    filter {
      prefix = "raw/"
    }
    
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    
    expiration {
      days = 365
    }
  }
  
  # Processed zone - transition to IA after 60 days
  rule {
    id     = "processed-zone-lifecycle"
    status = "Enabled"
    
    filter {
      prefix = "processed/"
    }
    
    transition {
      days          = 60
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 180
      storage_class = "GLACIER"
    }
  }
  
  # Curated zone - keep in Standard for fast access
  rule {
    id     = "curated-zone-lifecycle"
    status = "Enabled"
    
    filter {
      prefix = "curated/"
    }
    
    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }
  }
  
  # Athena results - delete after 7 days
  rule {
    id     = "athena-results-cleanup"
    status = "Enabled"
    
    filter {
      prefix = "athena-results/"
    }
    
    expiration {
      days = 7
    }
  }
}

# Scripts bucket for Glue jobs
resource "aws_s3_bucket" "scripts" {
  bucket = "${var.project_name}-scripts-${var.environment}"
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-scripts-${var.environment}"
  })
}

resource "aws_s3_bucket_versioning" "scripts" {
  bucket = aws_s3_bucket.scripts.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "scripts" {
  bucket = aws_s3_bucket.scripts.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "scripts" {
  bucket = aws_s3_bucket.scripts.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Logs bucket
resource "aws_s3_bucket" "logs" {
  bucket = "${var.project_name}-logs-${var.environment}"
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-logs-${var.environment}"
  })
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id
  
  rule {
    id     = "delete-old-logs"
    status = "Enabled"
    
    expiration {
      days = 90
    }
  }
}
