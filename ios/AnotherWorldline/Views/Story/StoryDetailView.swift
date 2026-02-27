import SwiftUI

struct StoryDetailView: View {
    let story: Story
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            ScrollView {
                VStack(spacing: 20) {
                    // Header
                    HStack {
                        Spacer()
                        Button(action: { dismiss() }) {
                            Image(systemName: "xmark.circle.fill")
                                .font(.title2)
                                .foregroundColor(.gray)
                        }
                    }
                    .padding()

                    // Genre badge
                    Text(story.genre)
                        .font(.system(size: 14, weight: .bold, design: .monospaced))
                        .foregroundColor(.black)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 6)
                        .background(genreColor(story.genre))
                        .cornerRadius(20)

                    // Worldline info
                    Text("제\(story.worldlineNumber)세계선 · \(story.sequenceNumber)번째 이야기")
                        .font(.system(size: 12, design: .monospaced))
                        .foregroundColor(.gray)

                    // Story content
                    Text(story.content)
                        .font(.system(size: 16, design: .serif))
                        .foregroundColor(.white)
                        .lineSpacing(8)
                        .padding(.horizontal, 24)
                        .padding(.vertical, 20)

                    // Stat changes
                    if let changes = story.statChanges, !changes.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("능력치 변동")
                                .font(.system(size: 14, weight: .bold, design: .monospaced))
                                .foregroundColor(.cyan)

                            ForEach(changes.sorted(by: { $0.key < $1.key }), id: \.key) { stat, change in
                                if change != 0 {
                                    HStack {
                                        Text(statName(stat))
                                            .font(.system(size: 12, design: .monospaced))
                                            .foregroundColor(.gray)
                                        Spacer()
                                        Text(change > 0 ? "+\(change)" : "\(change)")
                                            .font(.system(size: 14, weight: .bold, design: .monospaced))
                                            .foregroundColor(change > 0 ? .green : .red)
                                    }
                                }
                            }
                        }
                        .padding(.horizontal, 24)
                        .padding()
                        .background(Color.white.opacity(0.05))
                        .cornerRadius(12)
                        .padding(.horizontal, 24)
                    }

                    Spacer(minLength: 40)
                }
            }
        }
    }

    private func genreColor(_ genre: String) -> Color {
        switch genre {
        case "판타지": return .purple
        case "로맨스": return .pink
        case "스릴러": return .red
        case "히어로": return .orange
        case "SF": return .cyan
        case "수필": return .green
        case "시나리오": return .yellow
        default: return .gray
        }
    }

    private func statName(_ key: String) -> String {
        switch key {
        case "hp": return "체력"
        case "mp": return "마나"
        case "strength": return "힘"
        case "intelligence": return "지능"
        case "agility": return "민첩"
        case "luck": return "행운"
        case "charm": return "매력"
        default: return key
        }
    }
}
