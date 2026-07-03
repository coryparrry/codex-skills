# JVM, Gradle, Maven

## Detection Artifacts

- `settings.gradle`
- `settings.gradle.kts`
- `build.gradle`
- `build.gradle.kts`
- `pom.xml`
- `gradlew`
- `mvnw`

## Common Repo Shapes

- Gradle app or library
- Maven module or multi-module build
- mixed JVM workspace with module-specific checks

## Required Lifecycle Gates

- setup/bootstrap: wrapper-aware dependency resolution such as `./gradlew help`, `./gradlew tasks`, or `mvn -q -v`
- focused test: `./gradlew test` or `mvn test`
- full validation/CI: `./gradlew check`, `mvn verify`, lint, and build packaging when configured

## Native Commands

- `./gradlew test`
- `./gradlew check`
- `./gradlew build`
- `mvn test`
- `mvn verify`
- `mvn package`

## CI Expectations

CI should honor the wrapper scripts and run the same Gradle or Maven gate documented for local use.

## Package Boundary Rules

Multi-module builds should map commands to the module or aggregate root that actually owns the check.

## Common False Positives

- Do not ignore `gradlew` or `mvnw` when wrapper scripts exist.
- Do not require both Gradle and Maven coverage in the same repo.

## Severity Guidance

Missing test or verify gates in a shipped JVM app is usually P2. Missing wrapper use in docs can be P2 when it blocks repeatable builds.

## Good Finding Examples

- P2 scoped to `service-api`: `build.gradle` exists, but no `./gradlew test` or `mvn test` path is documented for the module.

## Bad Finding Examples

- P2 at root: repo lacks a `mvn test` finding even though `./mvnw test` is the actual documented path.
