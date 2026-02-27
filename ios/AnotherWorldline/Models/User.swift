import Foundation

struct User: Codable, Identifiable {
    let id: String
    let phoneNumber: String
    let nickname: String?
    let couponBalance: Int
    let dailyFreePullsUsed: Int

    enum CodingKeys: String, CodingKey {
        case id
        case phoneNumber = "phone_number"
        case nickname
        case couponBalance = "coupon_balance"
        case dailyFreePullsUsed = "daily_free_pulls_used"
    }
}
