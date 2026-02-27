import SwiftUI

struct CharacterStatsView: View {
    let character: GameCharacter

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Character header
                VStack(spacing: 8) {
                    Image(systemName: "person.circle.fill")
                        .font(.system(size: 60))
                        .foregroundColor(.cyan)

                    Text(character.name)
                        .font(.system(size: 24, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)

                    HStack(spacing: 12) {
                        Label(character.race, systemImage: "sparkle")
                            .font(.system(size: 12, design: .monospaced))
                            .foregroundColor(.purple)

                        Label("제\(character.worldlineCount)세계선", systemImage: "globe")
                            .font(.system(size: 12, design: .monospaced))
                            .foregroundColor(.cyan)
                    }

                    // Rarity
                    HStack {
                        Text("희귀도")
                            .font(.system(size: 12, design: .monospaced))
                            .foregroundColor(.gray)
                        Text(String(format: "%.1f%%", character.rarityScore))
                            .font(.system(size: 16, weight: .bold, design: .monospaced))
                            .foregroundColor(rarityColor(character.rarityScore))
                    }
                }
                .padding(.top, 20)

                // Stats
                VStack(alignment: .leading, spacing: 12) {
                    Text("능력치")
                        .font(.system(size: 14, weight: .bold, design: .monospaced))
                        .foregroundColor(.cyan)

                    statBar("체력", value: character.stats.hp, maxValue: 999, color: .red)
                    statBar("마나", value: character.stats.mp, maxValue: 999, color: .blue)
                    statBar("힘", value: character.stats.strength, maxValue: 100, color: .orange)
                    statBar("지능", value: character.stats.intelligence, maxValue: 100, color: .purple)
                    statBar("민첩", value: character.stats.agility, maxValue: 100, color: .green)
                    statBar("행운", value: character.stats.luck, maxValue: 100, color: .yellow)
                    statBar("매력", value: character.stats.charm, maxValue: 100, color: .pink)
                }
                .padding()
                .background(Color.white.opacity(0.05))
                .cornerRadius(12)
                .padding(.horizontal, 16)

                // Skills
                if !character.skills.isEmpty {
                    sectionView("스킬", items: character.skills, icon: "bolt.fill", color: .yellow)
                }

                // Pets
                if !character.pets.isEmpty {
                    sectionView("펫", items: character.pets, icon: "pawprint.fill", color: .green)
                }

                Spacer(minLength: 40)
            }
        }
        .background(Color.black)
    }

    private func statBar(_ name: String, value: Int, maxValue: Int, color: Color) -> some View {
        HStack {
            Text(name)
                .font(.system(size: 12, design: .monospaced))
                .foregroundColor(.gray)
                .frame(width: 40, alignment: .leading)

            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(Color.white.opacity(0.1))
                        .frame(height: 8)
                        .cornerRadius(4)

                    Rectangle()
                        .fill(color)
                        .frame(width: geometry.size.width * CGFloat(min(value, maxValue)) / CGFloat(maxValue), height: 8)
                        .cornerRadius(4)
                }
            }
            .frame(height: 8)

            Text("\(value)")
                .font(.system(size: 12, weight: .bold, design: .monospaced))
                .foregroundColor(.white)
                .frame(width: 40, alignment: .trailing)
        }
    }

    private func sectionView(_ title: String, items: [String], icon: String, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.system(size: 14, weight: .bold, design: .monospaced))
                .foregroundColor(.cyan)

            FlowLayout(spacing: 8) {
                ForEach(items, id: \.self) { item in
                    Label(item, systemImage: icon)
                        .font(.system(size: 12, design: .monospaced))
                        .foregroundColor(color)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(color.opacity(0.15))
                        .cornerRadius(16)
                }
            }
        }
        .padding()
        .background(Color.white.opacity(0.05))
        .cornerRadius(12)
        .padding(.horizontal, 16)
    }

    private func rarityColor(_ score: Double) -> Color {
        switch score {
        case 90...: return .yellow
        case 70..<90: return .purple
        case 50..<70: return .cyan
        case 30..<50: return .green
        default: return .gray
        }
    }
}

// Simple flow layout for tags
struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = arrange(proposal: proposal, subviews: subviews)
        return result.size
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = arrange(proposal: proposal, subviews: subviews)
        for (index, position) in result.positions.enumerated() {
            subviews[index].place(at: CGPoint(x: bounds.minX + position.x, y: bounds.minY + position.y), proposal: .unspecified)
        }
    }

    private func arrange(proposal: ProposedViewSize, subviews: Subviews) -> (size: CGSize, positions: [CGPoint]) {
        let maxWidth = proposal.width ?? .infinity
        var positions: [CGPoint] = []
        var x: CGFloat = 0
        var y: CGFloat = 0
        var maxHeight: CGFloat = 0

        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)
            if x + size.width > maxWidth, x > 0 {
                x = 0
                y += maxHeight + spacing
                maxHeight = 0
            }
            positions.append(CGPoint(x: x, y: y))
            maxHeight = max(maxHeight, size.height)
            x += size.width + spacing
        }

        return (CGSize(width: maxWidth, height: y + maxHeight), positions)
    }
}
