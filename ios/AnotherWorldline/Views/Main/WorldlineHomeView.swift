import SwiftUI

struct WorldlineHomeView: View {
    @State private var worldlineNumber = 1
    @State private var pullsRemaining = 3
    @State private var isPulling = false
    @State private var latestStory: Story?
    @State private var showStory = false

    var body: some View {
        NavigationStack {
            ZStack {
                Color.black.ignoresSafeArea()

                VStack(spacing: 24) {
                    // Worldline counter
                    VStack(spacing: 4) {
                        Text("제\(worldlineNumber)세계선")
                            .font(.system(size: 28, weight: .bold, design: .monospaced))
                            .foregroundColor(.cyan)

                        Text("Another Worldline")
                            .font(.system(size: 12, design: .monospaced))
                            .foregroundColor(.gray)
                    }
                    .padding(.top, 20)

                    Spacer()

                    // Globe placeholder (pixel art style)
                    ZStack {
                        Circle()
                            .fill(
                                RadialGradient(
                                    gradient: Gradient(colors: [.cyan.opacity(0.3), .purple.opacity(0.1), .clear]),
                                    center: .center,
                                    startRadius: 20,
                                    endRadius: 120
                                )
                            )
                            .frame(width: 240, height: 240)

                        Image(systemName: "globe.asia.australia.fill")
                            .font(.system(size: 100))
                            .foregroundStyle(
                                LinearGradient(
                                    colors: [.cyan, .blue, .purple],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                    }

                    Spacer()

                    // Pull button
                    VStack(spacing: 12) {
                        Button(action: { Task { await pullStory() } }) {
                            HStack(spacing: 12) {
                                if isPulling {
                                    ProgressView()
                                        .tint(.black)
                                } else {
                                    Image(systemName: "sparkles")
                                    Text("세계선 뽑기")
                                }
                            }
                            .font(.system(size: 20, weight: .bold, design: .monospaced))
                            .foregroundColor(.black)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 16)
                            .background(
                                LinearGradient(
                                    colors: [.cyan, .blue],
                                    startPoint: .leading,
                                    endPoint: .trailing
                                )
                            )
                            .cornerRadius(12)
                        }
                        .disabled(isPulling)
                        .padding(.horizontal, 32)

                        Text("오늘 남은 무료 뽑기: \(pullsRemaining)/3")
                            .font(.system(size: 12, design: .monospaced))
                            .foregroundColor(.gray)
                    }
                    .padding(.bottom, 32)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .sheet(isPresented: $showStory) {
                if let story = latestStory {
                    StoryDetailView(story: story)
                }
            }
        }
    }

    private func pullStory() async {
        isPulling = true
        // TODO: Call API
        // Simulated delay for now
        try? await Task.sleep(nanoseconds: 2_000_000_000)
        isPulling = false

        // TODO: Show actual story
        // showStory = true
    }
}

#Preview {
    WorldlineHomeView()
}
