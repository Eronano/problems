#include <iostream>
#include <ctime>
#include <vector>
#define ll long long
using namespace std;
void solve() {
    int n, k;
    cin >> n >> k;
    vector<int> v(n);
    for(auto &it : v) cin >> it;
    for(auto &it : v){
        if(it == 0) return cout << 1 << '\n', void();
    }
    long long l = 1, r = 9e18;
    while(l < r){
        ll mid = (l + r) >> 1, cnt = 0;
        for(int i = 0; i < n; ++i){
            cnt += mid / v[i];
            if(mid % v[i]) cnt++;
            if(cnt >= k) break;
        }
        if(cnt < k) l = mid + 1;
        else r = mid;
    }
    cout << l << '\n';
}
//=====================================
signed main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    //=====================================
    int t;
    cin >> t;
    while(t--) solve();
    //=====================================
    return 0;
}