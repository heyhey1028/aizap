dep-bff: ## Install dependencies for ts
	@cd app/bff && pnpm install

.PHONY: ci-ts
ci-ts: ## Run lint, format, type-check, and test for ts
	@make lint-ts
	@make format-ts
	@make type-check-ts
	@make test-ts

.PHONY: lint-ts
lint-ts: ## Run lint for ts
	@cd app/bff && pnpm lint

.PHONY: format-ts	
format-ts:
	@cd app/bff && pnpm format

.PHONY: type-check-ts
type-check-ts: ## Run type-check for ts
	@cd app/bff && pnpm type-check

.PHONY: test-ts
test-ts: ## Run test for ts
	@cd app/bff && pnpm test

# generate help from comment
.PHONY: help
help: ## Display this help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'