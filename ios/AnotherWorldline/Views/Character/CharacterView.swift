import SwiftUI

struct CharacterView: View {
    @State private var character: GameCharacter?
    @State private var showCreateSheet = false
    @State private var characterName = ""

    var body: some View {
        NavigationStack {
            ZStack {
                Color.black.ignoresSafeArea()

                if let character = character {
                    CharacterStatsView(character: character)
                } else {
                    // No character yet
                    VStack(spacing: 20) {
                        Image(systemName: "person.crop.circle.badge.plus")
                            .font(.system(size: 60))
                            .foregroundColor(.gray)

                        Text("캐릭터가 없습니다")
                            .font(.system(size: 18, design: .monospaced))
                            .foregroundColor(.gray)

                        Button("캐릭터 생성") {
                            showCreateSheet = true
                        }
                        .font(.system(size: 16, weight: .bold, design: .monospaced))
                        .foregroundColor(.black)
                        .padding(.horizontal, 32)
                        .padding(.vertical, 12)
                        .background(Color.cyan)
                        .cornerRadius(8)
                    }
                }
            }
            .navigationTitle("캐릭터")
            .navigationBarTitleDisplayMode(.inline)
            .sheet(isPresented: $showCreateSheet) {
                CreateCharacterSheet(characterName: $characterName) {
                    Task { await createCharacter() }
                }
            }
        }
    }

    private func createCharacter() async {
        guard !characterName.isEmpty else { return }
        do {
            character = try await APIClient.shared.createCharacter(name: characterName)
            showCreateSheet = false
        } catch {
            print("Error creating character: \(error)")
        }
    }
}

struct CreateCharacterSheet: View {
    @Binding var characterName: String
    let onCreate: () -> Void
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            ZStack {
                Color.black.ignoresSafeArea()

                VStack(spacing: 24) {
                    Text("새 캐릭터의 이름을 정해주세요")
                        .font(.system(size: 14, design: .monospaced))
                        .foregroundColor(.gray)

                    TextField("캐릭터 이름", text: $characterName)
                        .textFieldStyle(.plain)
                        .font(.system(size: 24, design: .monospaced))
                        .foregroundColor(.white)
                        .multilineTextAlignment(.center)
                        .padding()
                        .background(Color.white.opacity(0.1))
                        .cornerRadius(8)
                        .padding(.horizontal, 32)

                    Button(action: onCreate) {
                        Text("생성하기")
                            .font(.system(size: 16, weight: .bold, design: .monospaced))
                            .foregroundColor(.black)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.cyan)
                            .cornerRadius(8)
                    }
                    .disabled(characterName.isEmpty)
                    .padding(.horizontal, 32)
                }
            }
            .navigationTitle("캐릭터 생성")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("취소") { dismiss() }
                        .foregroundColor(.cyan)
                }
            }
        }
    }
}

#Preview {
    CharacterView()
}
