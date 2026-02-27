import SwiftUI

struct RankingView: View {
    @State private var rankings: [RankingEntry] = []
    @State private var myRank: Int?
    @State private var isLoading = false

    var body: some View {
        NavigationStack {
            ZStack {
                Color.black.ignoresSafeArea()

                if isLoading {
                    ProgressView()
                        .tint(.cyan)
                } else if rankings.isEmpty {
                    VStack(spacing: 12) {
                        Image(systemName: "trophy")
                            .font(.system(size: 40))
                            .foregroundColor(.gray)
                        Text("아직 랭킹이 없습니다")
                            .font(.system(size: 14, design: .monospaced))
                            .foregroundColor(.gray)
                    }
                } else {
                    ScrollView {
                        LazyVStack(spacing: 8) {
                            // My rank banner
                            if let myRank = myRank {
                                HStack {
                                    Text("내 순위")
                                        .font(.system(size: 12, design: .monospaced))
                                        .foregroundColor(.gray)
                                    Spacer()
                                    Text("#\(myRank)")
                                        .font(.system(size: 20, weight: .bold, design: .monospaced))
                                        .foregroundColor(.cyan)
                                }
                                .padding()
                                .background(Color.cyan.opacity(0.1))
                                .cornerRadius(12)
                                .padding(.horizontal, 16)
                            }

                            ForEach(rankings) { entry in
                                RankingRow(entry: entry)
                            }
                        }
                        .padding(.vertical, 8)
                    }
                }
            }
            .navigationTitle("랭킹")
            .navigationBarTitleDisplayMode(.inline)
            .task {
                await loadRankings()
            }
        }
    }

    private func loadRankings() async {
        isLoading = true
        do {
            let response = try await APIClient.shared.getRankings()
            rankings = response.rankings
            myRank = response.myRank
        } catch {
            print("Error loading rankings: \(error)")
        }
        isLoading = false
    }
}

struct RankingRow: View {
    let entry: RankingEntry

    var body: some View {
        HStack(spacing: 12) {
            // Rank number
            Text("#\(entry.rank)")
                .font(.system(size: 16, weight: .bold, design: .monospaced))
                .foregroundColor(rankColor)
                .frame(width: 40)

            // Character info
            VStack(alignment: .leading, spacing: 2) {
                Text(entry.characterName)
                    .font(.system(size: 14, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)

                HStack(spacing: 8) {
                    Text(entry.race)
                        .font(.system(size: 10, design: .monospaced))
                        .foregroundColor(.purple)

                    if let nickname = entry.userNickname {
                        Text("by \(nickname)")
                            .font(.system(size: 10, design: .monospaced))
                            .foregroundColor(.gray)
                    }
                }
            }

            Spacer()

            // Stats
            VStack(alignment: .trailing, spacing: 2) {
                Text(String(format: "%.1f%%", entry.rarityScore))
                    .font(.system(size: 14, weight: .bold, design: .monospaced))
                    .foregroundColor(.cyan)

                Text("\(entry.worldlineCount) 세계선")
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundColor(.gray)
            }
        }
        .padding()
        .background(Color.white.opacity(0.05))
        .cornerRadius(8)
        .padding(.horizontal, 16)
    }

    private var rankColor: Color {
        switch entry.rank {
        case 1: return .yellow
        case 2: return .gray
        case 3: return .orange
        default: return .white
        }
    }
}

#Preview {
    RankingView()
}
