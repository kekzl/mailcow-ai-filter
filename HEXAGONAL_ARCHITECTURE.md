# Hexagonal Architecture Refactoring Guide

## Overview

This project has been refactored to use **Hexagonal Architecture (Ports & Adapters)** with **Domain-Driven Design (DDD)** principles. This creates a clean separation of concerns and makes the codebase more maintainable, testable, and adaptable.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Core                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Domain Layer (Business Logic)              │ │
│  │  ✅ Email (Entity)                                      │ │
│  │  ✅ SieveFilter (Entity/Aggregate Root)                 │ │
│  │  ✅ FilterRule (Value Object)                           │ │
│  │  ✅ FilterCondition (Value Object)                      │ │
│  │  ✅ FilterAction (Value Object)                         │ │
│  │  ✅ EmailAddress (Value Object)                         │ │
│  │  ✅ EmailPattern (Value Object)                         │ │
│  │  ⏳ FilterGenerator (Domain Service) - TODO             │ │
│  │  ⏳ PatternDetector (Domain Service) - TODO             │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            Application Layer (Use Cases)                │ │
│  │  ⏳ AnalyzeEmailsUseCase - TODO                         │ │
│  │  ⏳ GenerateFilterUseCase - TODO                        │ │
│  │  ⏳ TestFilterUseCase - TODO                            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
         │                                        │
         ▼                                        ▼
┌──────────────────┐                    ┌──────────────────┐
│   Input Ports    │                    │  Output Ports    │
│  (Interfaces)    │                    │  (Interfaces)    │
├──────────────────┤                    ├──────────────────┤
│ ⏳ IEmailRepo     │                    │ ⏳ IEmailFetcher │
│ ⏳ IFilterRepo    │                    │ ⏳ ILLMService   │
└──────────────────┘                    └──────────────────┘
         │                                        │
         ▼                                        ▼
┌──────────────────┐                    ┌──────────────────┐
│     Adapters     │                    │     Adapters     │
│   (Primary)      │                    │   (Secondary)    │
├──────────────────┤                    ├──────────────────┤
│ ⏳ CLIAdapter     │                    │ 🔄 IMAPAdapter   │
│                  │                    │ 🔄 OllamaAdapter │
└──────────────────┘                    └──────────────────┘

Legend:
✅ Completed
⏳ TODO
🔄 Needs refactoring to use new architecture
```

## What Has Been Built

### ✅ Domain Layer (Complete)

#### Value Objects (`src/domain/value_objects/`)
All value objects are **immutable** and enforce domain rules:

1. **EmailAddress** - Email validation with domain extraction
   ```python
   email = EmailAddress("user@domain.com")
   print(email.domain)  # "domain.com"
   ```

2. **FilterCondition** - Represents a single filter condition
   ```python
   condition = FilterCondition.header_contains("subject", "Invoice")
   condition = FilterCondition.address_domain_is("from", "amazon.com")
   condition = FilterCondition.from_pattern("from:@paypal.com")
   ```

3. **FilterAction** - Represents an action to perform
   ```python
   action = FilterAction.fileinto("Work")
   action = FilterAction.mark_as_read()
   action = FilterAction.stop()
   ```

4. **FilterRule** - Combines conditions and actions
   ```python
   rule = FilterRule.create(
       conditions=[condition1, condition2],
       actions=[action1, action2],
       logical_operator="anyof",
       name="Work Emails",
       description="Filter work-related emails"
   )
   ```

5. **EmailPattern** - Detected patterns from AI analysis
   ```python
   pattern = EmailPattern.from_domain("amazon.com", confidence=0.95)
   pattern = EmailPattern.from_subject_keyword("invoice", confidence=0.85)
   ```

#### Entities (`src/domain/entities/`)

1. **Email** - Aggregate root for email messages
   ```python
   email = Email.create(
       sender="user@example.com",
       recipients=["recipient@example.com"],
       subject="Test Email",
       body="Email content",
       folder="INBOX"
   )

   if email.is_from_domain("example.com"):
       print("From example.com")
   ```

2. **SieveFilter** - Aggregate root for Sieve filters
   ```python
   filter = SieveFilter.create(
       name="Shopping Filter",
       description="Filters online shopping emails",
       rules=[rule1, rule2]
   )

   script = filter.to_sieve_script()
   is_valid, errors = filter.validate()
   ```

## Next Steps to Complete

### 1. Create Domain Services

Domain services contain business logic that doesn't naturally fit in entities or value objects.

**`src/domain/services/filter_generator.py`**:
```python
from typing import List
from ..entities.email import Email
from ..entities.sieve_filter import SieveFilter
from ..value_objects.email_pattern import EmailPattern

class FilterGenerator:
    """Domain service to generate filters from patterns."""

    def generate_from_patterns(
        self,
        patterns: List[EmailPattern],
        category_name: str,
        category_description: str
    ) -> SieveFilter:
        """Generate a SieveFilter from detected patterns."""
        # Convert patterns to conditions
        # Create rules with appropriate actions
        # Return SieveFilter entity
        pass
```

**`src/domain/services/pattern_detector.py`**:
```python
from typing import List
from ..entities.email import Email
from ..value_objects.email_pattern import EmailPattern

class PatternDetector:
    """Domain service to detect patterns in emails."""

    def detect_patterns(
        self,
        emails: List[Email]
    ) -> List[EmailPattern]:
        """Analyze emails to detect common patterns."""
        # Group by domains
        # Find common subject keywords
        # Calculate confidence scores
        # Return EmailPattern value objects
        pass
```

### 2. Create Application Layer

#### Ports (Interfaces)

**`src/application/ports/output/email_fetcher.py`**:
```python
from abc import ABC, abstractmethod
from typing import List
from src.domain.entities.email import Email

class IEmailFetcher(ABC):
    """Port for fetching emails from external sources."""

    @abstractmethod
    async def fetch_emails(
        self,
        folder: str,
        max_count: int,
        months_back: int
    ) -> List[Email]:
        """Fetch emails from a folder."""
        pass

    @abstractmethod
    async def get_folders(self) -> List[str]:
        """Get list of available folders."""
        pass
```

**`src/application/ports/output/llm_service.py`**:
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.domain.value_objects.email_pattern import EmailPattern

class ILLMService(ABC):
    """Port for LLM-based analysis."""

    @abstractmethod
    async def analyze_patterns(
        self,
        email_summaries: List[Dict[str, Any]]
    ) -> List[EmailPattern]:
        """Use LLM to detect patterns in emails."""
        pass
```

#### Use Cases

**`src/application/use_cases/analyze_emails.py`**:
```python
from dataclasses import dataclass
from typing import List
from ..ports.output.email_fetcher import IEmailFetcher
from ..ports.output.llm_service import ILLMService
from ...domain.services.pattern_detector import PatternDetector
from ...domain.value_objects.email_pattern import EmailPattern

@dataclass
class AnalyzeEmailsRequest:
    max_emails: int
    months_back: int
    folders_to_analyze: List[str]

@dataclass
class AnalyzeEmailsResponse:
    patterns: List[EmailPattern]
    total_emails_analyzed: int

class AnalyzeEmailsUseCase:
    """Use case for analyzing emails and detecting patterns."""

    def __init__(
        self,
        email_fetcher: IEmailFetcher,
        llm_service: ILLMService,
        pattern_detector: PatternDetector
    ):
        self.email_fetcher = email_fetcher
        self.llm_service = llm_service
        self.pattern_detector = pattern_detector

    async def execute(
        self,
        request: AnalyzeEmailsRequest
    ) -> AnalyzeEmailsResponse:
        """Execute the use case."""
        # 1. Fetch emails using email_fetcher port
        # 2. Use pattern_detector domain service
        # 3. Use llm_service for AI analysis
        # 4. Return response
        pass
```

### 3. Create Infrastructure Adapters

#### Refactor Existing Code as Adapters

**`src/infrastructure/adapters/secondary/imap/imap_adapter.py`**:
```python
from typing import List
from src.application.ports.output.email_fetcher import IEmailFetcher
from src.domain.entities.email import Email
# Import existing IMAPClient code

class IMAPAdapter(IEmailFetcher):
    """Adapter implementing IEmailFetcher using IMAP protocol."""

    def __init__(self, config: dict):
        # Initialize using existing IMAPClient
        pass

    async def fetch_emails(
        self,
        folder: str,
        max_count: int,
        months_back: int
    ) -> List[Email]:
        """Fetch emails and convert to domain Email entities."""
        # Use existing IMAP code
        # Convert to Email.create()
        pass
```

**`src/infrastructure/adapters/secondary/ollama/ollama_adapter.py`**:
```python
from typing import List, Dict, Any
from src.application.ports.output.llm_service import ILLMService
from src.domain.value_objects.email_pattern import EmailPattern
# Import existing Ollama code

class OllamaAdapter(ILLMService):
    """Adapter implementing ILLMService using Ollama."""

    async def analyze_patterns(
        self,
        email_summaries: List[Dict[str, Any]]
    ) -> List[EmailPattern]:
        """Analyze using Ollama and return EmailPattern value objects."""
        # Use existing Ollama code
        # Parse response into EmailPattern objects
        pass
```

#### CLI Adapter

**`src/infrastructure/adapters/primary/cli/cli_adapter.py`**:
```python
import typer
from src.application.use_cases.analyze_emails import (
    AnalyzeEmailsUseCase,
    AnalyzeEmailsRequest
)

app = typer.Typer()

@app.command()
def analyze(
    max_emails: int = 100,
    months_back: int = 12
):
    """Analyze emails and generate filters."""
    # Create use case with injected dependencies
    # Execute use case
    # Display results
    pass

if __name__ == "__main__":
    app()
```

### 4. Dependency Injection

**`src/infrastructure/config/dependency_injection.py`**:
```python
from src.application.use_cases.analyze_emails import AnalyzeEmailsUseCase
from src.infrastructure.adapters.secondary.imap.imap_adapter import IMAPAdapter
from src.infrastructure.adapters.secondary.ollama.ollama_adapter import OllamaAdapter
from src.domain.services.pattern_detector import PatternDetector

class Container:
    """Dependency injection container."""

    def __init__(self, config: dict):
        self.config = config

    def email_fetcher(self) -> IMAPAdapter:
        return IMAPAdapter(self.config['imap'])

    def llm_service(self) -> OllamaAdapter:
        return OllamaAdapter(self.config['ollama'])

    def pattern_detector(self) -> PatternDetector:
        return PatternDetector()

    def analyze_emails_use_case(self) -> AnalyzeEmailsUseCase:
        return AnalyzeEmailsUseCase(
            email_fetcher=self.email_fetcher(),
            llm_service=self.llm_service(),
            pattern_detector=self.pattern_detector()
        )
```

### 5. Update Main Entry Point

**`src/main.py`**:
```python
import asyncio
from infrastructure.config.dependency_injection import Container
from infrastructure.config.settings import load_config
from infrastructure.adapters.primary.cli.cli_adapter import app

async def main():
    # Load configuration
    config = load_config()

    # Create dependency injection container
    container = Container(config)

    # Run CLI with injected dependencies
    app()

if __name__ == "__main__":
    asyncio.run(main())
```

## Benefits of This Architecture

### 1. **Separation of Concerns**
- Domain logic is isolated from infrastructure
- Business rules are in one place
- Easy to understand and maintain

### 2. **Testability**
- Mock interfaces instead of concrete implementations
- Test domain logic without external dependencies
- Test use cases with fake adapters

### 3. **Flexibility**
- Swap IMAP for another protocol
- Change from Ollama to OpenAI
- Add REST API alongside CLI

### 4. **Type Safety**
- Strict typing with Python 3.13+
- Value objects prevent invalid data
- Compile-time error detection

### 5. **Domain-Driven Design**
- Business logic expressed in domain language
- Ubiquitous language in code
- Rich domain model

## Migration Strategy

### Phase 1: ✅ Complete (Current)
- Domain layer implemented
- Value objects and entities created
- Foundation established

### Phase 2: Domain Services (Next)
1. Create `FilterGenerator` domain service
2. Create `PatternDetector` domain service
3. Move pattern detection logic from AI analyzer

### Phase 3: Application Layer
1. Define port interfaces
2. Create use cases
3. Define DTOs for requests/responses

### Phase 4: Infrastructure Adapters
1. Refactor IMAPClient as IMAPAdapter
2. Refactor AIAnalyzer as OllamaAdapter
3. Create CLIAdapter
4. Set up dependency injection

### Phase 5: Integration
1. Wire everything together in main.py
2. Update Docker configuration
3. Write tests
4. Update documentation

## Testing Strategy

```
tests/
├── unit/
│   ├── domain/
│   │   ├── test_email.py
│   │   ├── test_sieve_filter.py
│   │   └── test_value_objects.py
│   ├── application/
│   │   └── test_use_cases.py
│   └── infrastructure/
│       └── test_adapters.py
├── integration/
│   ├── test_imap_integration.py
│   └── test_ollama_integration.py
└── e2e/
    └── test_end_to_end.py
```

### Example Tests

**`tests/unit/domain/test_email_address.py`**:
```python
import pytest
from src.domain.value_objects.email_address import EmailAddress

def test_valid_email():
    email = EmailAddress("user@example.com")
    assert email.value == "user@example.com"
    assert email.domain == "example.com"
    assert email.local_part == "user"

def test_invalid_email():
    with pytest.raises(ValueError):
        EmailAddress("invalid-email")

def test_domain_matching():
    email = EmailAddress("user@example.com")
    assert email.matches_domain("example.com")
    assert not email.matches_domain("other.com")
```

## References

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

## Summary

You now have a solid foundation with:
- ✅ Complete domain layer (value objects + entities)
- ✅ Clear architecture structure
- ✅ Type-safe, immutable value objects
- ✅ Rich domain models

Next steps are to implement domain services, application layer, and refactor existing code as adapters. This architecture will make your codebase more maintainable, testable, and professional.
