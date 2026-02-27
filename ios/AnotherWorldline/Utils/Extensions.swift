import SwiftUI

extension Color {
    static let worldlineCyan = Color(red: 0.0, green: 0.85, blue: 0.85)
    static let worldlinePurple = Color(red: 0.6, green: 0.2, blue: 0.9)
    static let worldlineDark = Color(red: 0.05, green: 0.05, blue: 0.1)
}

extension View {
    func pixelBorder(color: Color = .cyan, width: CGFloat = 2) -> some View {
        self.overlay(
            RoundedRectangle(cornerRadius: 4)
                .stroke(color, lineWidth: width)
        )
    }
}
