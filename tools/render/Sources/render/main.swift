import CoreGraphics
import Foundation
import ImageIO
import SwiftDraw
import UniformTypeIdentifiers

// render <lista> <lado>: cada línea de <lista> es «origen.svg<TAB>destino.png». Cada SVG se pinta con su lado mayor a <lado>
// píxeles, sobre transparente. Escribe «ok» o «fallo» por línea en la salida.
let arguments = Swift.CommandLine.arguments
let lines = (try? String(contentsOfFile: arguments[1], encoding: .utf8))?.split(separator: "\n") ?? []
let side = CGFloat(Double(arguments[2]) ?? 512)
let space = CGColorSpace(name: CGColorSpace.sRGB)!
for line in lines {
    let parts = line.split(separator: "\t").map(String.init)
    guard parts.count == 2 else { continue }
    autoreleasepool {
        guard let svg = SVG(fileURL: URL(fileURLWithPath: parts[0])), svg.size.width > 0, svg.size.height > 0 else {
            print("fallo\t\(parts[0])"); return
        }
        let scale = side / max(svg.size.width, svg.size.height)
        let width = max(1, Int((svg.size.width * scale).rounded())), height = max(1, Int((svg.size.height * scale).rounded()))
        guard let context = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8, bytesPerRow: 0, space: space,
                                      bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { print("fallo\t\(parts[0])"); return }
        // SwiftDraw dibuja con el origen arriba: se le da la vuelta al lienzo de Core Graphics.
        context.translateBy(x: 0, y: CGFloat(height))
        context.scaleBy(x: 1, y: -1)
        context.draw(svg, in: CGRect(x: 0, y: 0, width: CGFloat(width), height: CGFloat(height)))
        guard let image = context.makeImage(),
              let destination = CGImageDestinationCreateWithURL(URL(fileURLWithPath: parts[1]) as CFURL, UTType.png.identifier as CFString, 1, nil) else {
            print("fallo\t\(parts[0])"); return
        }
        CGImageDestinationAddImage(destination, image, nil)
        print(CGImageDestinationFinalize(destination) ? "ok\t\(parts[1])" : "fallo\t\(parts[0])")
    }
}
