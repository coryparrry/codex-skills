# Swift and Apple

## Detection Artifacts

- `Package.swift`
- `Sources/`
- `Tests/`
- `.xcodeproj`
- `.xcworkspace`
- `xcodebuild`

## Common Repo Shapes

- SwiftPM package
- Apple app project with an Xcode workspace
- mixed package plus app target layout

## Required Lifecycle Gates

- setup/bootstrap: `swift package resolve`, Xcode dependency resolution, or documented equivalent
- focused test: `swift test` or scheme-scoped `xcodebuild test`
- full validation/CI: build, test, and platform-specific checks when the repo ships an app or framework

## Native Commands

- `swift build`
- `swift test`
- `xcodebuild`
- `xcodebuild test`
- `swift-format`
- `swiftlint`

## CI Expectations

CI should use the same package or scheme commands the repo documents locally, including platform SDK selection when needed.

## Package Boundary Rules

Treat a pure SwiftPM package differently from an Xcode app project. Apple app targets may need scheme and destination selection that SwiftPM packages do not.

## Common False Positives

- Do not require `xcodebuild` for a pure SwiftPM package.
- Do not require an app runtime command for a library package.

## Severity Guidance

Missing tests in a shipped Apple app or framework is usually P2. Missing scheme or SDK documentation can be P1 when it blocks CI or release work.

## Good Finding Examples

- P2 scoped to `Package.swift`: a SwiftPM package exists, but no `swift test` or equivalent gate is documented.

## Bad Finding Examples

- P2 at root: repo lacks an Xcode scheme wrapper even though the repo is pure SwiftPM.
