// swift-tools-version: 6.0
import PackageDescription

// Convierte los logos SVG de Picons en PNG de alta resolución (con SwiftDraw, licencia Zlib).
let package = Package(
    name: "render",
    platforms: [.macOS(.v14)],
    dependencies: [.package(url: "https://github.com/swhitty/SwiftDraw.git", exact: "0.29.0")],
    targets: [.executableTarget(name: "render", dependencies: [.product(name: "SwiftDraw", package: "SwiftDraw")])]
)
