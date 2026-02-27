import SwiftUI

struct OnboardingView: View {
    @EnvironmentObject var authManager: AuthManager
    @State private var phoneNumber = ""
    @State private var verificationCode = ""
    @State private var showVerification = false
    @State private var isLoading = false
    @State private var errorMessage: String?

    var body: some View {
        ZStack {
            // Pixel art style background
            Color.black.ignoresSafeArea()

            VStack(spacing: 32) {
                Spacer()

                // Title
                VStack(spacing: 8) {
                    Text("다른 세계선")
                        .font(.system(size: 36, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)

                    Text("Another Worldline")
                        .font(.system(size: 14, design: .monospaced))
                        .foregroundColor(.gray)

                    Text("✦ 매일 AI가 써주는 나만의 멀티버스 소설 ✦")
                        .font(.system(size: 12, design: .monospaced))
                        .foregroundColor(.cyan)
                        .padding(.top, 4)
                }

                Spacer()

                // Auth form
                VStack(spacing: 16) {
                    if !showVerification {
                        // Phone input
                        VStack(alignment: .leading, spacing: 8) {
                            Text("전화번호")
                                .font(.system(size: 12, design: .monospaced))
                                .foregroundColor(.gray)

                            TextField("010-1234-5678", text: $phoneNumber)
                                .textFieldStyle(.plain)
                                .font(.system(size: 18, design: .monospaced))
                                .foregroundColor(.white)
                                .padding()
                                .background(Color.white.opacity(0.1))
                                .cornerRadius(8)
                                .keyboardType(.phonePad)
                        }

                        Button(action: { Task { await sendCode() } }) {
                            HStack {
                                if isLoading {
                                    ProgressView()
                                        .tint(.black)
                                } else {
                                    Text("인증번호 받기")
                                }
                            }
                            .font(.system(size: 16, weight: .bold, design: .monospaced))
                            .foregroundColor(.black)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.cyan)
                            .cornerRadius(8)
                        }
                        .disabled(phoneNumber.isEmpty || isLoading)
                    } else {
                        // Verification code input
                        VStack(alignment: .leading, spacing: 8) {
                            Text("인증번호 6자리")
                                .font(.system(size: 12, design: .monospaced))
                                .foregroundColor(.gray)

                            TextField("000000", text: $verificationCode)
                                .textFieldStyle(.plain)
                                .font(.system(size: 24, design: .monospaced))
                                .foregroundColor(.white)
                                .padding()
                                .background(Color.white.opacity(0.1))
                                .cornerRadius(8)
                                .keyboardType(.numberPad)
                                .multilineTextAlignment(.center)
                        }

                        Button(action: { Task { await verifyCode() } }) {
                            HStack {
                                if isLoading {
                                    ProgressView()
                                        .tint(.black)
                                } else {
                                    Text("세계선 입장 ▶")
                                }
                            }
                            .font(.system(size: 16, weight: .bold, design: .monospaced))
                            .foregroundColor(.black)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.cyan)
                            .cornerRadius(8)
                        }
                        .disabled(verificationCode.count != 6 || isLoading)
                    }

                    if let error = errorMessage {
                        Text(error)
                            .font(.system(size: 12, design: .monospaced))
                            .foregroundColor(.red)
                    }
                }
                .padding(.horizontal, 32)

                Spacer()
            }
        }
    }

    private func sendCode() async {
        isLoading = true
        errorMessage = nil
        do {
            let code = try await authManager.register(phoneNumber: phoneNumber)
            showVerification = true
            // In dev mode, auto-fill the code
            #if DEBUG
            verificationCode = code
            #endif
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    private func verifyCode() async {
        isLoading = true
        errorMessage = nil
        do {
            try await authManager.verify(phoneNumber: phoneNumber, code: verificationCode)
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }
}

#Preview {
    OnboardingView()
        .environmentObject(AuthManager())
}
