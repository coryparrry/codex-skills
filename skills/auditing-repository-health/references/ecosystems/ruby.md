# Ruby

## Detection Artifacts

- `Gemfile`
- `Gemfile.lock`
- `*.gemspec`
- `Rakefile`
- `.ruby-version`

## Common Repo Shapes

- gem
- Rails or Rack app
- script or tooling repo with Rake tasks

## Required Lifecycle Gates

- setup/bootstrap: `bundle install` or documented equivalent
- focused test: `bundle exec rspec`, `bundle exec rake test`, or a package-specific test task
- full validation/CI: test plus lint or build tasks when the repo ships code

## Native Commands

- `bundle exec rake`
- `bundle exec rspec`
- `bundle exec ruby -Itest`
- `bundle exec rubocop`

## CI Expectations

CI should run the same Bundler-aware commands the repo documents locally.

## Package Boundary Rules

Use gemspecs and Rake tasks as package-level signals even when the repo root also has application code.

## Common False Positives

- Do not require npm-style scripts in a Ruby repo.
- Do not require a server command for a gem or library-only repository.

## Severity Guidance

Missing tests in a shipped gem or app is usually P2. Missing Bundler setup instructions can be P1 when it blocks contributors.

## Good Finding Examples

- P2 scoped to `gems/reporting`: `Gemfile` exists, but no documented `bundle exec rspec` or Rake test task covers the gem.

## Bad Finding Examples

- P2 at root: repo lacks `npm test` even though it is a Ruby app with Bundler and Rake.
