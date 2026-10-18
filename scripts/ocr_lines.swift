import Foundation
import Vision
import AppKit
// 使い方: ocr_lines a.png b.png ... → JSON 1行1画像 {"f":名前,"w":W,"h":H,"lines":[{"t":文字,"b":[x0,y0,x1,y1]}]}（画素・左上原点）
for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
    let W = Double(cg.width), H = Double(cg.height)
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.recognitionLanguages = ["ja-JP", "en-US"]
    req.usesLanguageCorrection = false
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    var lines: [[String: Any]] = []
    for r in req.results ?? [] {
        guard let c = r.topCandidates(1).first, c.confidence > 0.3 else { continue }
        let b = r.boundingBox
        lines.append(["t": c.string, "b": [Int(b.minX*W), Int((1-b.maxY)*H), Int(b.maxX*W), Int((1-b.minY)*H)]])
    }
    let o: [String: Any] = ["f": (path as NSString).lastPathComponent, "w": Int(W), "h": Int(H), "lines": lines]
    if let d = try? JSONSerialization.data(withJSONObject: o), let s = String(data: d, encoding: .utf8) { print(s) }
}
