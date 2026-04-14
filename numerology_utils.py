# ...
from db_access import (
    get_wuku_awal_map as _db_get_wuku_awal_map,
    get_wewaran_entry as _db_get_wewaran_entry,
    get_rejeki as _db_get_rejeki,
    get_rejeki_pq as _db_get_rejeki_pq,
    get_tenung_deskripsi as _db_get_tenung_deskripsi,
    get_bridge_details as _db_get_bridge_details,
    get_bridge_name as _db_get_bridge_name,
    get_karmic_debt as _db_get_karmic_debt_desc,
)

def weton_calculation(date_str: str) -> dict:
    from datetime import datetime, date
    def _parse(ds: str):
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
            try:
                return datetime.strptime((ds or '').strip(), fmt).date()
            except Exception:
                continue
        return None
    d = _parse(date_str)
    if not d:
        return {}
    hari_list = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']
    hari = hari_list[d.weekday()]
    base = date(1633,7,8)
    diff = (d - base).days
    pasaran_list = ['Umanis','Pahing','Pon','Wage','Kliwon']
    pasaran = pasaran_list[diff % 5]
    neptu_hari = {'Senin':4,'Selasa':3,'Rabu':7,'Kamis':8,'Jumat':6,'Sabtu':9,'Minggu':5}.get(hari,0)
    neptu_pas = {'Umanis':5,'Pahing':9,'Pon':7,'Wage':4,'Kliwon':8}.get(pasaran,0)
    neptu = neptu_hari + neptu_pas
    # Determine Wuku using annual anchor (first Sunday) and wuku_awal.xlsx
    wuku = _calculate_wuku_from_annual_anchor(d)
    return {'hari': hari, 'pasaran': pasaran, 'neptu': neptu, 'wuku': wuku}

def get_wuku_names() -> list:
    """Return the canonical ordered list of 30 Wuku names used by calculations.

    Keeping this single source of truth ensures UI dropdowns and DB sync stay consistent
    with the computation fallback in _calculate_wuku_from_annual_anchor().
    """
    return [
        'Sinta','Landep','Ukir','Kurantil','Tolu','Gumbreg','Wariga','Warigadian','Julungwangi','Sungsang',
        'Dunggulan','Kuningan','Langkir','Medangsia','Pujut','Pahang','Krulut','Merakih','Tambir','Medangkungan',
        'Matal','Uye','Menail','Perangbakat','Bala','Ugu','Wayang','Kelawu','Dukut','Watugunung'
    ]

def _get_first_sunday(year: int):
    """Return date of the first Sunday for the given year."""
    from datetime import date, timedelta
    d = date(year, 1, 1)
    # Python weekday: Mon=0..Sun=6; compute days to next Sunday incl. same day
    days_since_sun = (d.weekday() + 1) % 7
    first_sun = d + timedelta(days=(0 if days_since_sun == 0 else (7 - days_since_sun)))
    return first_sun

def _load_wuku_awal_map():
    """Load mapping: year -> {no_wuku, wuku_awal} from SQLite.
    Cached on function attribute to avoid reloading.
    """
    if hasattr(_load_wuku_awal_map, 'cache'):
        return _load_wuku_awal_map.cache
    try:
        mapping = _db_get_wuku_awal_map()
    except Exception:
        mapping = {}
    _load_wuku_awal_map.cache = mapping
    return mapping

def _calculate_wuku_from_annual_anchor(d):
    """Calculate Wuku name for date d based on annual first Sunday anchor and wuku_awal.xlsx.
    Rules:
    - Find first Sunday of the relevant anchor year. If date is before that Sunday, use previous year anchor.
    - Each Wuku lasts 7 days from Sunday..Saturday. Advance by number of weeks from the anchor Sunday.
    - Start Wuku for the anchor year taken from wuku_awal.xlsx: 'no_wuku' (1..30) or 'wuku_awal' name.
    - If Excel not found, fallback to epoch 1633-07-08 with Sinta as start.
    """
    from datetime import timedelta, date
    # Wuku names in order
    wuku_names = [
        'Sinta','Landep','Ukir','Kurantil','Tolu','Gumbreg','Wariga','Warigadian','Julungwangi','Sungsang',
        'Dunggulan','Kuningan','Langkir','Medangsia','Pujut','Pahang','Krulut','Merakih','Tambir','Medangkungan',
        'Matal','Uye','Menail','Perangbakat','Bala','Ugu','Wayang','Kelawu','Dukut','Watugunung'
    ]

    # Determine the Sunday (start of week) for the given date
    days_since_sun = (d.weekday() + 1) % 7
    week_sun = d - timedelta(days=days_since_sun)

    # Determine anchor year: year of first Sunday not after the date's Sunday
    first_sun_this = _get_first_sunday(d.year)
    if week_sun >= first_sun_this:
        anchor_year = d.year
        anchor_sunday = first_sun_this
    else:
        anchor_year = d.year - 1
        anchor_sunday = _get_first_sunday(anchor_year)

    # Load mapping from Excel
    mapping = _load_wuku_awal_map()

    # Resolve starting wuku index (0-based)
    start_idx = 0  # default Sinta
    if anchor_year in mapping:
        entry = mapping[anchor_year]
        no_wuku = entry.get('no_wuku')
        name = entry.get('wuku_awal', '')
        if isinstance(no_wuku, int) and 1 <= no_wuku <= 30:
            start_idx = (no_wuku - 1) % 30
        elif isinstance(name, str) and name:
            try:
                start_idx = wuku_names.index(name.strip().capitalize())
            except ValueError:
                start_idx = 0
    else:
        # Fallback: special-case 1633 epoch
        if anchor_year == 1633:
            start_idx = 0

    # Weeks since anchor Sunday
    weeks = max(0, (week_sun - anchor_sunday).days // 7)
    idx = (start_idx + weeks) % 30
    return wuku_names[idx]

# --- Restored utility and calculation functions required by app.py ---

def life_path_calculation(date_str: str) -> dict:
    from datetime import datetime
    def _parse(ds: str):
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
            try:
                return datetime.strptime((ds or '').strip(), fmt)
            except Exception:
                continue
        return None
    def _reduce(n: int) -> int:
        while n > 9 and n not in (11, 22):
            n = sum(int(d) for d in str(n))
        return int(n)
    dt = _parse(date_str)
    if not dt:
        return {'life_path': 0}
    total = sum(int(d) for d in dt.strftime('%Y%m%d'))
    return {'life_path': _reduce(total)}

def get_life_path_details(life_path: int) -> dict:
    return {'deskripsi': f'Deskripsi Life Path {life_path}', 'detail': '', 'kekuatan': [], 'tantangan': []}

def compute_challenges(date_str: str) -> dict:
    """Compute simple challenge numbers and components from a birth date.
    Returns a dict with keys:
      - numbers: list of length 4 [C1, C2, C3, C4] (some may be 0 if not computed)
      - components: {'M': month_reduced, 'Y': year_reduced}

    This is a minimal implementation to satisfy app.py's expectations for C4 and components.
    """
    from datetime import datetime

    def reduce_1_9(n: int) -> int:
        n = abs(int(n))
        while n > 9:
            n = sum(int(d) for d in str(n))
        return max(1, n)

    # Parse date in common formats
    dt = None
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y'):
        try:
            dt = datetime.strptime((date_str or '').strip(), fmt)
            break
        except Exception:
            continue
    if not dt:
        # Fallback: use today to avoid breaking the flow
        dt = datetime.now()

    # Components
    month_val = int(dt.strftime('%m'))
    year_val = int(dt.strftime('%Y'))
    M = reduce_1_9(month_val)
    # Reduce the sum of year digits
    Y = reduce_1_9(sum(int(d) for d in str(year_val)))

    # Compute a simple C4 as |M - Y| reduced
    C4 = reduce_1_9(abs(M - Y))
    # Leave C1..C3 as 0 for now (can be expanded later)
    numbers = [0, 0, 0, C4]

    return {
        'numbers': numbers,
        'components': {'M': M, 'Y': Y}
    }

def heart_desire_calculation(name: str) -> dict:
    """Calculate Heart's Desire number from vowels in name using A1Z26 method.
    
    Heart's Desire represents inner desires, motivations, and what the soul yearns for.
    Uses only vowels (A, E, I, O, U) and reduces to single digit (1-9).
    """
    vowels = 'AEIOU'
    
    # Extract vowels and convert to A1Z26 values
    vowel_letters = [ch.upper() for ch in (name or '') if ch.upper() in vowels]
    
    if not vowel_letters:
        return {'number': 0, 'vowels': [], 'sum': 0}
    
    # A1Z26 values: A=1, B=2, C=3, ..., Z=26
    vowel_values = [ord(ch) - ord('A') + 1 for ch in vowel_letters]
    total_sum = sum(vowel_values)
    
    # Reduce to single digit (1-9)
    reduced = total_sum
    while reduced > 9:
        reduced = sum(int(d) for d in str(reduced))
    
    return {
        'number': reduced,
        'vowels': vowel_letters,
        'vowel_values': vowel_values,
        'sum': total_sum
    }


def personality_calculation(name: str) -> dict:
    """Calculate Personality number from consonants in name using Pythagorean numerology mapping.
    
    Personality represents how others see you, your outer self and first impressions.
    Uses only consonants (all letters except A, E, I, O, U) and reduces to single digit (1-9)
    or preserves master numbers (11, 22).
    
    Pythagorean mapping:
    A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9,
    J=1, K=2, L=3, M=4, N=5, O=6, P=7, Q=8, R=9,
    S=1, T=2, U=3, V=4, W=5, X=6, Y=7, Z=8
    """
    vowels = 'AEIOU'
    
    def pythagorean_value(ch: str) -> int:
        """Convert letter to Pythagorean value (A=1, B=2, ..., I=9, J=1, K=2, ...)"""
        val = ord(ch.upper()) - ord('A') + 1  # A=1, B=2, ..., Z=26
        return ((val - 1) % 9) + 1  # Reduce to 1..9 cycle
    
    # Extract consonants and convert to Pythagorean values
    consonant_letters = [ch.upper() for ch in (name or '') if ch.isalpha() and ch.upper() not in vowels]
    
    if not consonant_letters:
        return {'number': 0, 'consonants': [], 'sum': 0}
    
    # Pythagorean values: cycle through 1-9
    consonant_values = [pythagorean_value(ch) for ch in consonant_letters]
    total_sum = sum(consonant_values)
    
    # Reduce to single digit (1-9) or preserve master numbers (11, 22)
    reduced = total_sum
    while reduced > 22:
        reduced = sum(int(d) for d in str(reduced))
    
    # If it's not 11 or 22 and still > 9, continue reducing
    if reduced not in (11, 22) and reduced > 9:
        while reduced > 9:
            reduced = sum(int(d) for d in str(reduced))
    
    return {
        'number': reduced,
        'consonants': consonant_letters,
        'consonant_values': consonant_values,
        'sum': total_sum
    }


def karakter_calculation(birth_date: str) -> dict:
    """Calculate Karakter (character) from birth date using specific A-Z mapping.
    
    Maps birth date digits to letters A-H, then calculates derived values I-Z.
    Returns O (Root Number) as single digit and M&N combination as 2-digit string.
    
    Formula:
    A = first digit of day, B = second digit of day
    C = first digit of month, D = second digit of month  
    E = first digit of year, F = second digit of year
    G = third digit of year, H = fourth digit of year
    I = A+B (Sektor Ayah), J = C+D (Sektor Ayah)
    K = E+F (Sektor Ibu), L = G+H (Sektor Ibu)
    M = I+J, N = K+L, O = M+N (Root Number)
    P = N+O, Q = M+O, R = P+Q (Rejeki Number)
    S = I+M, T = J+M, U = K+N, V = L+N
    W = O+P, X = P+R, Y = O+Q, Z = Q+R
    """
    from datetime import datetime
    
    def reduce_to_single_digit(n: int) -> int:
        """Reduce number to single digit (1-9, where 0 becomes 5)."""
        n = abs(int(n))
        if n == 0:
            return 5
        while n > 9:
            n = sum(int(d) for d in str(n))
        return n if n != 0 else 5
    
    # Parse birth date
    dt = None
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y'):
        try:
            dt = datetime.strptime((birth_date or '').strip(), fmt)
            break
        except Exception:
            continue
    
    if not dt:
        return {'error': 'Invalid date format'}
    
    # Get padded components
    DD = dt.strftime('%d')  # 2 digits
    MM = dt.strftime('%m')  # 2 digits  
    YYYY = dt.strftime('%Y')  # 4 digits
    
    # A-H: Individual digits
    A = int(DD[0])
    B = int(DD[1])
    C = int(MM[0])
    D = int(MM[1])
    E = int(YYYY[0])
    F = int(YYYY[1])
    G = int(YYYY[2])
    H = int(YYYY[3])
    
    # I-L: Sector calculations (reduced to single digits)
    I = reduce_to_single_digit(A + B)  # Sektor Ayah
    J = reduce_to_single_digit(C + D)  # Sektor Ayah
    K = reduce_to_single_digit(E + F)  # Sektor Ibu
    L = reduce_to_single_digit(G + H)  # Sektor Ibu
    
    # M-O: Core calculations
    M = I + J
    N = K + L
    O = M + N  # Root Number
    
    # P-R: Rejeki calculations
    P = N + O
    Q = M + O
    R = P + Q  # Rejeki Number
    
    # S-Z: Extended calculations
    S = I + M
    T = J + M
    U = K + N
    V = L + N
    W = O + P
    X = P + R
    Y = O + Q
    Z = Q + R
    
    # Reduce O to single digit for mapping
    O_reduced = reduce_to_single_digit(O)
    
    # Reduce M and N to single digits, then combine as 2-digit string
    M_reduced = reduce_to_single_digit(M)
    N_reduced = reduce_to_single_digit(N)
    MN_combination = f"{M_reduced}{N_reduced}"
    
    return {
        'birth_date': dt.strftime('%d/%m/%Y'),
        'components': {
            'DD': DD, 'MM': MM, 'YYYY': YYYY
        },
        'digits': {
            'A': A, 'B': B, 'C': C, 'D': D,
            'E': E, 'F': F, 'G': G, 'H': H
        },
        'sectors': {
            'I': I, 'J': J, 'K': K, 'L': L
        },
        'core': {
            'M': M, 'N': N, 'O': O, 'O_reduced': O_reduced,
            'M_reduced': M_reduced, 'N_reduced': N_reduced
        },
        'rejeki': {
            'P': P, 'Q': Q, 'R': R
        },
        'extended': {
            'S': S, 'T': T, 'U': U, 'V': V,
            'W': W, 'X': X, 'Y': Y, 'Z': Z
        },
        'mapping_keys': {
            'O_key': str(O_reduced),
            'MN_key': MN_combination
        }
    }


def tenung_karma_calculation(birth_date: str) -> dict:
    """Calculate Tenung Karma combination using complex N-DL-D formula.
    
    This is completely separate from karakter_calculation with its own formula.
    
    Args:
        birth_date: Date string in format 'YYYY-MM-DD'
    
    Returns:
        Dict with karma_combination, individual values, and mapping key
    """
    from datetime import datetime
    
    try:
        # Parse birth date
        if isinstance(birth_date, str):
            dt = datetime.strptime(birth_date, '%Y-%m-%d')
        else:
            dt = birth_date
    except Exception as e:
        return {'error': f'Invalid birth date format: {e}'}
    
    # Helper function for reduction (reduce if > 22, keep if <= 22)
    def reduce_karma(n: int) -> int:
        if n <= 22:
            return n
        while n > 22:
            n = sum(int(digit) for digit in str(n))
            if n <= 22:
                break
        return n
    
    # Basic calculations - A, B tidak direduksi, C direduksi jika > 22
    A = sum(int(digit) for digit in dt.strftime('%d'))  # Jumlah tanggal (tidak direduksi)
    B = sum(int(digit) for digit in dt.strftime('%m'))  # Jumlah bulan (tidak direduksi)
    C_raw = sum(int(digit) for digit in dt.strftime('%Y'))  # Jumlah tahun raw
    C = reduce_karma(C_raw)  # Tahun direduksi jika > 22
    
    # Primary calculations
    D = A + B + C
    E = A + B + C + D
    
    # Secondary calculations
    f = B + C
    g = C + D
    h = A + D
    i = A + B
    j = B + E
    k = f + E
    l = C + E
    
    # Tertiary calculations
    m = reduce_karma(reduce_karma(reduce_karma(D + E)) + l)  # n + l (where n = D + E)
    n = reduce_karma(D + E)
    o = reduce_karma(h + E)
    
    # Quaternary calculations
    P = reduce_karma(A + E)
    q = reduce_karma(i + E)
    r = reduce_karma(l + m)
    s = reduce_karma(m + n)
    
    # Final level calculations
    al = reduce_karma(A + P)
    bl = reduce_karma(B + j)
    cl = reduce_karma(C + l)
    dl = reduce_karma(D + n)
    fl = reduce_karma(f + k)
    gl = reduce_karma(g + m)
    hl = reduce_karma(h + o)
    il = reduce_karma(i + P)
    
    # Apply reduction to calculated values only (A, B, C stay as original sums)
    # A, B, C are NOT reduced - they stay as original digit sums
    D = reduce_karma(D)
    E = reduce_karma(E)
    f = reduce_karma(f)
    g = reduce_karma(g)
    h = reduce_karma(h)
    i = reduce_karma(i)
    j = reduce_karma(j)
    k = reduce_karma(k)
    l = reduce_karma(l)
    m = reduce_karma(m)
    n = reduce_karma(n)
    o = reduce_karma(o)
    P = reduce_karma(P)
    q = reduce_karma(q)
    r = reduce_karma(r)
    s = reduce_karma(s)
    
    # Final N-DL-D combination
    # Based on the pattern, using key values for the combination
    N_final = n  # n value
    DL_final = dl  # dl value  
    D_final = D  # D value
    
    # Create combination string for database mapping
    karma_combination = f"{N_final}-{DL_final}-{D_final}"
    
    return {
        'karma_combination': karma_combination,
        'N': N_final,
        'DL': DL_final,
        'D': D_final,
        'mapping_key': karma_combination,
        # Include all calculated values for debugging/display
        'all_values': {
            'A': A, 'B': B, 'C': C, 'D': D, 'E': E,
            'f': f, 'g': g, 'h': h, 'i': i, 'j': j,
            'k': k, 'l': l, 'm': m, 'n': n, 'o': o,
            'P': P, 'q': q, 'r': r, 's': s,
            'al': al, 'bl': bl, 'cl': cl, 'dl': dl,
            'fl': fl, 'gl': gl, 'hl': hl, 'il': il
        },
        'birth_breakdown': {
            'date_sum': A, 'month_sum': B, 'year_sum': C, 'year_raw': C_raw
        }
    }


def prediksi_calculation(birth_date: str) -> dict:
    """Calculate predictions from birth date using complex matrix conditions.
    
    Uses the same A-Z calculation as karakter_calculation but applies 
    specific condition matching for predictions.
    """
    # Reuse the karakter calculation to get all values
    karakter_data = karakter_calculation(birth_date)
    
    if 'error' in karakter_data:
        return karakter_data
    
    # Extract all calculated values
    digits = karakter_data['digits']
    sectors = karakter_data['sectors']
    core = karakter_data['core']
    rejeki = karakter_data['rejeki']
    extended = karakter_data['extended']
    
    A, B, C, D, E, F, G, H = digits['A'], digits['B'], digits['C'], digits['D'], digits['E'], digits['F'], digits['G'], digits['H']
    I, J, K, L = sectors['I'], sectors['J'], sectors['K'], sectors['L']
    M, N, O = core['M'], core['N'], core['O']
    P, Q, R = rejeki['P'], rejeki['Q'], rejeki['R']
    S, T, U, V, W, X, Y, Z = extended['S'], extended['T'], extended['U'], extended['V'], extended['W'], extended['X'], extended['Y'], extended['Z']
    
    # List to store matched conditions
    matched_conditions = []
    
    # Helper function to check conditions and add matches
    def check_condition(condition_str: str, condition_result: bool):
        if condition_result:
            matched_conditions.append(condition_str)
    
    # Apply all the matrix conditions from your specification
    
    # Single digit conditions
    check_condition("I=1", I == 1)
    check_condition("N=1", N == 1)
    check_condition("J=1", J == 1)
    check_condition("J=2", J == 2)
    check_condition("K=1", K == 1)
    check_condition("L=2", L == 2)
    check_condition("I=2", I == 2)
    check_condition("N=2", N == 2)
    check_condition("I=3", I == 3)
    check_condition("N=3", N == 3)
    check_condition("I=4", I == 4)
    check_condition("N=4", N == 4)
    check_condition("I=5", I == 5)
    check_condition("N=5", N == 5)
    check_condition("I=6", I == 6)
    check_condition("N=6", N == 6)
    check_condition("I=7", I == 7)
    check_condition("N=7", N == 7)
    check_condition("I=8", I == 8)
    check_condition("N=8", N == 8)
    check_condition("I=9", I == 9)
    check_condition("N=9", N == 9)
    
    # Two digit combinations
    check_condition("KL=1", K*10 + L == 1)
    check_condition("JK=11", J*10 + K == 11)
    check_condition("NO=22", N*10 + O == 22)
    check_condition("IJ=12", I*10 + J == 12)
    check_condition("KL=12", K*10 + L == 12)
    check_condition("KN=12", K*10 + N == 12)
    check_condition("IJ=13", I*10 + J == 13 or I*10 + J == 31)
    check_condition("KL=13", K*10 + L == 13 or K*10 + L == 31)
    check_condition("KL=14", K*10 + L == 14 or K*10 + L == 41)
    check_condition("KL=15", K*10 + L == 15 or K*10 + L == 51)
    check_condition("JK=16", J*10 + K == 16)
    check_condition("JK=61", J*10 + K == 61)
    check_condition("KL=16", K*10 + L == 16)
    check_condition("KL=61", K*10 + L == 61)
    check_condition("KL=17", K*10 + L == 17)
    check_condition("KL=18", K*10 + L == 18)
    check_condition("KL=19", K*10 + L == 19)
    check_condition("KN=21", K*10 + N == 21)
    check_condition("KL=21", K*10 + L == 21)
    check_condition("IJ=21", I*10 + J == 21)
    check_condition("KL=24", K*10 + L == 24 or K*10 + L == 42)
    check_condition("KL=26", K*10 + L == 26 or K*10 + L == 62)
    check_condition("IJ=33", I*10 + J == 33)
    check_condition("JN=44", J*10 + N == 44)
    check_condition("JM=44", J*10 + M == 44)
    check_condition("MO=44", M*10 + O == 44)
    check_condition("JM=66", J*10 + M == 66)
    check_condition("NO=66", N*10 + O == 66)
    check_condition("NO=77", N*10 + O == 77)
    check_condition("MO=77", M*10 + O == 77)
    check_condition("IM=78", I*10 + M == 78 or I*10 + M == 87)
    check_condition("MO=78", M*10 + O == 78 or M*10 + O == 87)
    check_condition("IJ=57", I*10 + J == 57 or I*10 + J == 75)
    check_condition("IJ=52", I*10 + J == 52)
    check_condition("JK=21", J*10 + K == 21)
    
    # Three digit combinations
    check_condition("IJK=111", I*100 + J*10 + K == 111)
    check_condition("JKL=111", J*100 + K*10 + L == 111)
    check_condition("LNO=123", L*100 + N*10 + O == 123)
    check_condition("JKL=115", J*100 + K*10 + L == 115)
    check_condition("JNO=222", J*100 + N*10 + O == 222)
    check_condition("IMO=444", I*100 + M*10 + O == 444)
    check_condition("JNO=555", J*100 + N*10 + O == 555)
    check_condition("ILO=666", I*100 + L*10 + O == 666)
    check_condition("IMO=888", I*100 + M*10 + O == 888)
    check_condition("KMO=888", K*100 + M*10 + O == 888)
    check_condition("JNO=888", J*100 + N*10 + O == 888)
    check_condition("MNL=426", M*100 + N*10 + L == 426)
    check_condition("IMN=642", I*100 + M*10 + N == 642)
    check_condition("JMN=642", J*100 + M*10 + N == 642)
    
    # Four digit combinations
    check_condition("IJKL=1111", I*1000 + J*100 + K*10 + L == 1111)
    check_condition("IKMN=1111", I*1000 + K*100 + M*10 + N == 1111)
    check_condition("IJKM=1911", I*1000 + J*100 + K*10 + M == 1911)
    check_condition("JMNO=1911", J*1000 + M*100 + N*10 + O == 1911)
    check_condition("JNOT=5555", J*1000 + N*100 + O*10 + T == 5555)
    
    # Five digit combinations
    check_condition("IMOPU=11111", I*10000 + M*1000 + O*100 + P*10 + U == 11111)
    check_condition("IMOTP=33333", I*10000 + M*1000 + O*100 + T*10 + P == 33333)
    check_condition("JNOTQ=44444", J*10000 + N*1000 + O*100 + T*10 + Q == 44444)
    check_condition("IJMNO=44444", I*10000 + J*1000 + M*100 + N*10 + O == 44444)
    check_condition("JONTQ=55555", J*10000 + O*1000 + N*100 + T*10 + Q == 55555)
    check_condition("JNOTQ=77777", J*10000 + N*1000 + O*100 + T*10 + Q == 77777)
    
    # Special range conditions (ST and VW combinations are not reduced)
    # S, T, V, W are individual values (can be reduced), but ST and VW combinations are not reduced
    ST_combination = S*10 + T  # 2-digit combination, not reduced
    VW_combination = V*10 + W  # 2-digit combination, not reduced
    check_condition("ST-VW=69-96", (ST_combination == 69 and VW_combination == 96))
    
    # Six digit conditions (>5 means more than 5 of the same digit)
    def count_digit_occurrences(digit, values_list):
        return sum(1 for v in values_list if v == digit)
    
    all_values = [I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z]
    
    check_condition(">5=111111", count_digit_occurrences(1, all_values) > 5)
    check_condition(">5=222222", count_digit_occurrences(2, all_values) > 5)
    check_condition(">6=333333", count_digit_occurrences(3, all_values) > 5)
    check_condition(">5=444444", count_digit_occurrences(4, all_values) > 5)
    check_condition(">5=555555", count_digit_occurrences(5, all_values) > 5)
    check_condition(">5=666666", count_digit_occurrences(6, all_values) > 5)
    check_condition(">5=777777", count_digit_occurrences(7, all_values) > 5)
    check_condition(">5=888888", count_digit_occurrences(8, all_values) > 5)
    check_condition(">5=999999", count_digit_occurrences(9, all_values) > 5)
    
    return {
        'birth_date': karakter_data['birth_date'],
        'all_values': {
            'I': I, 'J': J, 'K': K, 'L': L, 'M': M, 'N': N, 'O': O,
            'P': P, 'Q': Q, 'R': R, 'S': S, 'T': T, 'U': U, 'V': V,
            'W': W, 'X': X, 'Y': Y, 'Z': Z
        },
        'matched_conditions': matched_conditions,
        'total_matches': len(matched_conditions)
    }


def harani_calculation(name: str) -> dict:
    """Hitung angka Harani dari nama dengan metode Pythagoras bertetangga.
    
    Aturan:
    - Huruf A..Z dipetakan ke nilai Pythagoras: A=1,B=2,C=3,D=4,E=5,F=6,G=7,H=8,I=9,J=1,K=2,...
    - Bangun segitiga bilangan: next[i] = reduce_to_single_digit_or_keep_master(cur[i] + cur[i+1]).
    - Nilai 11 dan 22 dipertahankan (tidak direduksi). Selain itu, reduksi ke satu digit (1..9).
    - Hasil akhir (elemen tunggal) adalah angka Harani.
    """
    def pythagoras_value(ch: str) -> int:
        """Convert letter to Pythagoras value (A=1, B=2, ..., I=9, J=1, K=2, ...)"""
        val = ord(ch.upper()) - ord('A') + 1  # A=1, B=2, ..., Z=26
        return ((val - 1) % 9) + 1  # Reduce to 1..9 cycle

    def reduce_to_single_digit(n: int) -> int:
        """Reduce number to single digit (1..9) using modulo-9 rule (0 -> 9)."""
        n = abs(int(n))
        if n == 0:
            return 0
        r = n % 9
        return 9 if r == 0 else r

    def reduce_to_single_digit_or_keep_master(n: int) -> int:
        """Preserve master numbers 11 and 22; otherwise reduce via modulo-9 mapping (0 -> 9)."""
        if n in (11, 22):
            return n
        return reduce_to_single_digit(n)

    # Extract letters and convert to Pythagoras values
    letters = [ch for ch in (name or '') if ch.isalpha()]
    base = [pythagoras_value(ch) for ch in letters]

    if not base:
        return {'number': 0}

    # Build triangle using neighbor sum method
    cur = base[:]
    while len(cur) > 1:
        nxt = []
        for i in range(len(cur) - 1):
            s = cur[i] + cur[i + 1]
            nxt.append(reduce_to_single_digit_or_keep_master(s))
        cur = nxt

    harani_number = cur[0]
    # Final check: if result is not master number and >9, reduce to single digit
    if harani_number not in (11, 22) and harani_number > 9:
        harani_number = reduce_to_single_digit(harani_number)

    return {'number': harani_number}

def karma_number_from_missing_digits(name: str) -> int:
    """Hitung angka karma dari huruf yang TIDAK muncul pada nama.

    Aturan:
    - Gunakan alfabet A..Z sebagai acuan.
    - Ambil huruf unik (A..Z) yang muncul pada `name` (abaikan selain huruf).
    - Huruf hilang = alfabet \ present.
    - Nilai huruf A1Z26 (A=1..Z=26), jumlahkan semua huruf hilang.
    - Reduksi ke 1..9 (digital root), kembalikan sebagai int (0 jika total <= 0).

    Catatan: Pemetaan ke deskripsi dilakukan di app.py via karma.xlsx.
    """
    try:
        present = set(ch.upper() for ch in (name or '') if ch.isalpha())
        alphabet = [chr(c) for c in range(ord('A'), ord('Z') + 1)]
        missing = [ch for ch in alphabet if ch not in present]

        total = sum((ord(ch) - 64) for ch in missing)

        def reduce_1_9(n: int) -> int:
            if n <= 0:
                return 0
            while n > 9:
                n = sum(int(d) for d in str(abs(n)))
            return n

        return reduce_1_9(total)
    except Exception:
        return 0

def rejeki_pythagoras_from_birthdate(date_str: str) -> dict:
    """Hitung Angka Rejeki berdasarkan pipeline A..Z yang diminta.

    Definisi digit:
    - A,B: digit 1 & 2 untuk tanggal (DD)
    - C,D: digit 1 & 2 untuk bulan (MM)
    - E,F,G,H: digit 1..4 untuk tahun (YYYY)

    Turunan:
    - I = A + B
    - J = C + D
    - K = E + F
    - L = G + H
    - M = I + J
    - N = K + L
    - O = M + N   (Root Number)
    - P = N + O   (digit pertama Rejeki)
    - Q = M + O   (digit kedua Rejeki)
    - R = P + Q   (Rejeki Number)
    - S = I + M, T = J + M, U = K + N, V = L + N,
      W = O + P, X = P + R, Y = O + Q, Z = Q + R

    Reduksi: P, Q, R direduksi ke 1..9 (jaga 0 jika memang nol). Nilai lain dikembalikan apa adanya.
    Deskripsi: Baca rejeki.xlsx bila tersedia untuk deskripsi berdasarkan R dan kombinasi PQ.
    """
    from datetime import datetime
    import os
    import pandas as pd

    # Helper reduce to 1..9 (keep 0)
    def reduce_1_9_or_0(n: int) -> int:
        try:
            n = int(n)
        except Exception:
            return 0
        if n == 0:
            return 0
        while n > 9:
            n = sum(int(d) for d in str(abs(n)))
        return n if n != 0 else 0

    # Parse date to components DD, MM, YYYY
    dt = None
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y'):
        try:
            dt = datetime.strptime((date_str or '').strip(), fmt)
            break
        except Exception:
            continue
    if not dt:
        # fallback ke today agar fungsi tidak error
        dt = datetime.now()

    DD = dt.strftime('%d')  # 2 digit
    MM = dt.strftime('%m')  # 2 digit
    YYYY = dt.strftime('%Y')  # 4 digit

    # A..H sesuai definisi
    A = int(DD[0])
    B = int(DD[1])
    C = int(MM[0])
    D = int(MM[1])
    E = int(YYYY[0])
    F = int(YYYY[1])
    G = int(YYYY[2])
    H = int(YYYY[3])

    # I..O
    I = A + B
    J = C + D
    K = E + F
    L = G + H
    M = I + J
    N = K + L
    O = M + N  # Root Number

    # P,Q,R (dengan reduksi 1..9 kecuali 0)
    P_raw = N + O
    Q_raw = M + O
    R_raw = P_raw + Q_raw
    P = reduce_1_9_or_0(P_raw)
    Q = reduce_1_9_or_0(Q_raw)
    # Angka Rejeki adalah reduksi dari nilai P dan Q
    R = reduce_1_9_or_0(P + Q)

    # S..Z (tanpa reduksi wajib; simpan apa adanya untuk referensi)
    S = I + M
    T = J + M
    U = K + N
    V = L + N
    W = O + P_raw
    X = P_raw + R_raw
    Y = O + Q_raw
    Z = Q_raw + R_raw

    # Siapkan hasil dasar
    result = {
        'rejeki': R,
        'P': P,
        'Q': Q,
        'root': O,
        'values': {
            'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F, 'G': G, 'H': H,
            'I': I, 'J': J, 'K': K, 'L': L, 'M': M, 'N': N, 'O': O,
            'P_raw': P_raw, 'Q_raw': Q_raw, 'R_raw': R_raw,
            'P': P, 'Q': Q, 'R': R,
            'S': S, 'T': T, 'U': U, 'V': V, 'W': W, 'X': X, 'Y': Y, 'Z': Z,
            'DD': int(DD), 'MM': int(MM), 'YYYY': int(YYYY)
        },
        'birth_date': dt.strftime('%d/%m/%Y'),
        'deskripsi': '',
        'deskripsi_p': '',
        'deskripsi_q': '',
        'deskripsi_pq': '',
    }

    # Muat deskripsi dari database (rejeki table)
    try:
        row_r = _db_get_rejeki(R)
        if row_r and row_r.get('deskripsi'):
            result['deskripsi'] = row_r['deskripsi']
        row_p = _db_get_rejeki(P)
        if row_p and row_p.get('deskripsi'):
            result['deskripsi_p'] = row_p['deskripsi']
        row_q = _db_get_rejeki(Q)
        if row_q and row_q.get('deskripsi'):
            result['deskripsi_q'] = row_q['deskripsi']
        # Combined P+Q
        key = f"{P}{Q}"
        pq_desc = _db_get_rejeki_pq(key)
        if pq_desc:
            result['deskripsi_pq'] = pq_desc
    except Exception:
        pass

    return result


def get_karmic_debt(reduced, precursor):
    """Standalone helper to drive Karmic Debt detection for one number.

    Args:
        reduced: The final single-digit value (e.g., 1, 4, 5, 7).
        precursor: The two-digit source used in reduction (e.g., 19, 13, 14, 16).

    Returns:
        dict with keys:
          - has_karmic_debt: bool
          - debt_double: int | None   # 13, 14, 16, or 19 when present
          - reduced: int | None
          - precursor: int | None
    """
    debt = karmic_debt_for(reduced, precursor)
    return {
        'has_karmic_debt': bool(debt),
        'debt_double': debt,
        'reduced': reduced,
        'precursor': precursor,
    }

# --- Wewaran calculators ---

def get_wewaran(wewaran_type: str, value: int) -> str:
    """Get Wewaran name based on type and calculated value from SQLite; fallback to hardcoded mapping."""
    try:
        entry = _db_get_wewaran_entry(wewaran_type, int(value))
        if entry and entry.get('nama'):
            nama = str(entry.get('nama')).strip()
            return 'Menga' if nama.lower() == 'menge' else nama
    except Exception as e:
        print(f"Error in get_wewaran (DB): {e}")
    # Fallback mapping
    wewaran_mapping = {
        'Ekawara': ['Void', 'Luang'],
        'Dwiwara': ['Menga', 'Pepet'],
        'Triwara': ['Pasah', 'Beteng', 'Kajeng'],
        'Caturwara': ['Sri', 'Laba', 'Jaya', 'Menala'],
        'Sadwara': ['Tungleh', 'Aryang', 'Urukung', 'Paniron', 'Was', 'Maulu'],
        'Astawara': ['Sri', 'Indra', 'Guru', 'Yama', 'Ludra', 'Brahma', 'Kala', 'Uma'],
        'Sangawara': ['Dangu', 'Jangur', 'Gigis', 'Nohan', 'Ogan', 'Erangan', 'Urungan', 'Tulus', 'Dadi'],
        'Dasawara': ['Pandita', 'Pati', 'Suka', 'Duka', 'Sri', 'Manuh', 'Manusa', 'Raja', 'Dewa', 'Raksasa']
    }
    if wewaran_type in wewaran_mapping:
        names = wewaran_mapping[wewaran_type]
        if 0 <= value < len(names):
            return names[value]
    return f"Unknown_{value}"

def calculate_ekawara(neptu_hari: int, neptu_pasaran: int) -> str:
    total = neptu_hari + neptu_pasaran
    # Ekawara logic: (Neptu_hari + neptu_pasaran) / 2
    # If result is even (genap) = "" (empty)
    # If result is odd (ganjil) = "Luang"
    if total % 2 == 0:  # Even (genap)
        return ""  # Empty string
    else:  # Odd (ganjil)
        return "Luang"

def calculate_dwiwara(neptu_hari: int, neptu_pasaran: int) -> str:
    total = neptu_hari + neptu_pasaran
    return get_wewaran('Dwiwara', (total % 2))  # 0..1

def calculate_triwara(wuku_num: int, day_num: int) -> str:
    w0 = max(0, wuku_num - 1)
    value = (w0 + day_num) % 3
    return get_wewaran('Triwara', value)  # 0..2

def calculate_caturwara(wuku_num: int, day_num: int, day_name: str) -> str:
    w0 = max(0, wuku_num - 1)
    # Rules for Caturwara calculation:
    # 1. If wuku_num <= 11 and day != "Senin": ((w0 * 7) + day_num) % 4
    # 2. If wuku_num == 11 and day == "Senin": ((w0 * 7) + 1 + day_num) % 4  
    # 3. If wuku_num > 11: ((w0 * 7) + day_num) % 4
    
    if wuku_num <= 11 and day_name != "Senin":
        # Rule 1: wuku <= 11 and not Monday
        value = ((w0 * 7) + 1 + day_num) % 4
    elif wuku_num == 11 and day_name == "Senin":
        # Rule 2: wuku == 11 and Monday
        value = ((w0 * 7) + 2 + day_num) % 4
    else:
        # Rule 3: wuku > 11 (or any other case)
        value = ((w0 * 7) + day_num) % 4
    
    # No conversion needed - use direct result
    
    return get_wewaran('Caturwara', value)  # 1-based: 1,2,3,0 maps to indices 1,2,3,0

def calculate_sadwara(wuku_num: int, day_num: int) -> str:
    w0 = max(0, wuku_num - 1)
    value = (w0 + day_num) % 6
    return get_wewaran('Sadwara', value)  # 0..5

def calculate_astawara(wuku_num: int, day_num: int, day_name: str) -> str:
    w0 = max(0, wuku_num - 1)
    # Option B (aligned with Caturwara style): base formula with a special case
    # Base: ((w0 * 7) + day_num) % 8
    # Additional rule: if wuku_num <= 11 and day_name != 'Senin', add +1
    # Special case: if wuku_num == 11 and day_name == 'Senin', add +2
    if wuku_num <= 11 and day_name != "Senin":
        value = ((w0 * 7) + 1 + day_num) % 8
    elif wuku_num == 11 and day_name == "Senin":
        value = ((w0 * 7) + 2 + day_num) % 8
    else:
        value = ((w0 * 7) + day_num) % 8
    return get_wewaran('Astawara', value)  # 0..7 (Excel uses 0-based indexing)

def calculate_sangawara(wuku_num: int, day_num: int) -> str:
    w0 = max(0, wuku_num - 1)
    # Formula based on verification with 16/01/1962
    value = ((w0 * 7) + day_num + 6) % 9
    return get_wewaran('Sangawara', value)  # 0..8

def calculate_dasawara(neptu_hari: int, neptu_pasaran: int) -> str:
    value = (neptu_hari + neptu_pasaran) % 10
    return get_wewaran('Dasawara', value)  # 0..9

def calculate_arah_sukses(date_str: str) -> dict:
    """Hitung Arah Sukses berdasarkan pipeline A..Z dan rumus skor arah yang diberikan.

    Output kompatibel dengan tampilan yang ada:
    - best_direction: nama arah dengan skor tertinggi
    - best_score: nilai skornya
    - direction_scores: dict {nama_arah: skor}
    - values: dict berisi A..Z, DD, MM, YYYY
    - steps: penjelasan langkah singkat
    - birth_date: tanggal dalam format DD/MM/YYYY
    """
    from datetime import datetime

    # Parse date flexibly
    dt = None
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y'):
        try:
            dt = datetime.strptime((date_str or '').strip(), fmt)
            break
        except Exception:
            continue
    if not dt:
        dt = datetime.now()

    # Ambil digit tanggal
    DD = dt.strftime('%d')  # 2 digit
    MM = dt.strftime('%m')  # 2 digit
    YYYY = dt.strftime('%Y')  # 4 digit

    # A..H sesuai arahan (digit dasar)
    A = int(DD[0])
    B = int(DD[1])
    C = int(MM[0])
    D = int(MM[1])
    E = int(YYYY[0])
    F = int(YYYY[1])
    G = int(YYYY[2])
    H = int(YYYY[3])

    # Helper reduksi 1..9 (abaikan master number, jadi tidak ada pengecualian 11/22)
    def red(n: int) -> int:
        try:
            n = int(n)
        except Exception:
            return 0
        if n == 0:
            return 0
        while n > 9:
            n = sum(int(d) for d in str(abs(n)))
        return n

    # I..Z sesuai arahan, setiap penjumlahan langsung direduksi 1..9
    I = red(A + B)
    J = red(C + D)
    K = red(E + F)
    L = red(G + H)
    M = red(I + J)
    N = red(K + L)
    O = red(M + N)  # Root Number
    P = red(N + O)  # Digit pertama Rejeki yang membentuk R
    Q = red(M + O)  # Digit kedua Rejeki yang membentuk R
    R = red(P + Q)  # Rejeki Number
    S = red(I + M)
    T = red(J + M)
    U = red(K + N)
    V = red(L + N)
    W = red(O + P)
    X = red(P + R)
    Y = red(O + Q)
    Z = red(Q + R)

    # Skor arah sesuai rumus
    # Catatan: Perbaiki penulisan "Barata Daya" -> "Barat Daya"
    skor_barat_laut = red(I + J + M)
    skor_utara = red(J + K)
    skor_timur_laut = red(K + L + N)
    skor_tenggara = red(L + N + O)
    skor_selatan = red(M + N + O)
    skor_barat_daya = red(I + M + O)
    skor_pusat = red(J + K + M + N)
    # Komposit
    skor_barat = red(skor_barat_laut + skor_barat_daya)
    skor_timur = red(skor_timur_laut + skor_tenggara)

    direction_scores = {
        'Barat Laut': skor_barat_laut,
        'Utara': skor_utara,
        'Timur Laut': skor_timur_laut,
        'Tenggara': skor_tenggara,
        'Selatan': skor_selatan,
        'Barat Daya': skor_barat_daya,
        'Pusat': skor_pusat,
        'Barat': skor_barat,
        'Timur': skor_timur,
    }

    # Tentukan arah terbaik
    best_direction = max(direction_scores.items(), key=lambda kv: kv[1])[0] if direction_scores else ''
    best_score = direction_scores.get(best_direction, 0)

    # Simpan nilai untuk debugging/tampilan
    values = {
        'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F, 'G': G, 'H': H,
        'I': I, 'J': J, 'K': K, 'L': L, 'M': M, 'N': N, 'O': O,
        'P': P, 'Q': Q, 'R': R, 'S': S, 'T': T, 'U': U, 'V': V,
        'W': W, 'X': X, 'Y': Y, 'Z': Z,
        'DD': int(DD), 'MM': int(MM), 'YYYY': int(YYYY)
    }

    steps = [
        f"Tanggal input = {dt.strftime('%d/%m/%Y')}",
        "Hitung A..H dari digit tanggal, bulan, tahun",
        "Hitung I..Z sesuai rumus dan setiap hasil dijadikan 1..9 (tanpa master number)",
        "Hitung skor arah (dan reduksi 1..9)",
        f"Arah terbaik = {best_direction} (skor {best_score})",
    ]

    return {
        'best_direction': best_direction,
        'best_score': best_score,
        'direction_scores': direction_scores,
        'values': values,
        'steps': steps,
        'birth_date': dt.strftime('%d/%m/%Y'),
    }

# --- Hutang Karma calculation ---

def calculate_hutang_karma(birth_date: str, name: str) -> dict:
    """Hitung Hutang Karma dan info pendukung untuk ditampilkan di template.

    Mengembalikan dict dengan kunci:
    - karma_number: int
    - karma_description: str
    - karma_meaning: str
    - karma_lesson: str
    - karma_advice: str
    - life_path: int
    - name_number: int (reduksi 1..9 dari A1Z26 nama)
    - calculation: {day, month, year, name_sum, total_sum}
    """
    from datetime import datetime
    import os
    import pandas as pd

    # Helper reduksi 1..9 (jaga 0 bila nol)
    def reduce_1_9_or_0(n: int) -> int:
        try:
            n = int(n)
        except Exception:
            return 0
        if n == 0:
            return 0
        while n > 9:
            n = sum(int(d) for d in str(abs(n)))
        return n

    # 1) Karma number dari nama (huruf yang hilang) — gunakan helper yang sudah ada
    try:
        karma_number = karma_number_from_missing_digits(name)
    except Exception:
        karma_number = 0

    # Helper: get first two-digit precursor in reduction chain and final reduced 1..9
    def _reduced_with_precursor(n: int):
        try:
            n = int(n)
        except Exception:
            return (0, None)
        
        # Track the first Karmic Debt number encountered during reduction
        precursor = None
        r = n
        
        # Check each step of reduction for KD numbers
        while r > 9:
            # Check if current number is a KD before reducing
            if precursor is None and r in [13, 14, 16, 19]:
                precursor = r
            # Reduce to next step
            r = sum(int(d) for d in str(r))
        
        # Also check if the initial number was a KD
        if precursor is None and n in [13, 14, 16, 19]:
            precursor = n
            
        return (r, precursor)

    # 2) Life Path dari tanggal lahir
    try:
        lp = life_path_calculation(birth_date).get('life_path', 0)
    except Exception:
        lp = 0

    # 3) Name number menggunakan Harani calculation (konsisten dengan harani_result)
    name_number_precursor = None
    try:
        harani_info = harani_calculation(name)
        name_number = harani_info.get('number', 0)
        
        # For Name Number Karmic Debt detection, use A1Z26 sum method
        clean = ''.join(ch.upper() for ch in (name or '') if ch.isalpha())
        name_sum_raw = sum((ord(ch) - 64) for ch in clean)
        # Check if A1Z26 sum has KD precursor before reduction
        name_number_from_a1z26, name_number_precursor = _reduced_with_precursor(name_sum_raw)
    except Exception:
        name_sum_raw = 0
        name_number = 0

    # 4) Komponen perhitungan tanggal untuk ditampilkan
    day_v = month_v = year_v = 0
    lp_total_digits = 0
    life_path_precursor = None
    try:
        dt = None
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y'):
            try:
                dt = datetime.strptime((birth_date or '').strip(), fmt)
                break
            except Exception:
                continue
        if dt is None:
            dt = datetime.now()
        day_v = sum(int(d) for d in dt.strftime('%d'))
        month_v = sum(int(d) for d in dt.strftime('%m'))
        year_v = sum(int(d) for d in dt.strftime('%Y'))
        
        # For Life Path Karmic Debt detection, use traditional method:
        # Reduce each component to single digit first, then sum
        day_reduced = reduce_1_9_or_0(day_v)
        month_reduced = reduce_1_9_or_0(month_v) 
        year_reduced = reduce_1_9_or_0(year_v)
        lp_total_digits = day_reduced + month_reduced + year_reduced
        lp_reduced_from_total, life_path_precursor = _reduced_with_precursor(lp_total_digits)
    except Exception:
        pass

    total_sum = day_v + month_v + year_v + name_sum_raw
    # Birthdate-only sum and reduced (as a birthdate-based karmic measure)
    birth_sum_only = day_v + month_v + year_v
    birth_karma_reduced, birth_karma_precursor = _reduced_with_precursor(birth_sum_only)

    # 5) Ambil deskripsi dari karma.xlsx bila ada
    karma_description = f"Hutang Karma {karma_number}"
    karma_meaning = ""
    karma_lesson = "Pelajaran hidup terkait pembelajaran batin dan kebiasaan yang perlu ditata."
    karma_advice = "Gunakan kesadaran, disiplin, dan empati untuk menyeimbangkan energi karmic."

    try:
        excel_path = os.path.join(os.path.dirname(__file__), 'karma.xlsx')
        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path)
            cols = {str(c).strip().lower(): c for c in df.columns}
            col_no = cols.get('no') or cols.get('kode') or cols.get('angka') or cols.get('karma')
            col_title = cols.get('judul') or cols.get('title') or cols.get('deskripsi_singkat') or cols.get('deskripsi')
            col_meaning = cols.get('arti') or cols.get('makna') or cols.get('meaning') or cols.get('deskripsi')
            col_lesson = cols.get('pelajaran') or cols.get('lesson')
            col_advice = cols.get('saran') or cols.get('advice')
            if col_no:
                try:
                    df[col_no] = pd.to_numeric(df[col_no], errors='coerce').astype('Int64')
                except Exception:
                    pass
                row = df.loc[df[col_no] == karma_number]
                if not row.empty:
                    if col_title and not pd.isna(row.iloc[0].get(col_title)):
                        karma_description = str(row.iloc[0][col_title]).strip() or karma_description
                    if col_meaning and not pd.isna(row.iloc[0].get(col_meaning)):
                        karma_meaning = str(row.iloc[0][col_meaning]).strip() or karma_meaning
                    if col_lesson and not pd.isna(row.iloc[0].get(col_lesson)):
                        karma_lesson = str(row.iloc[0][col_lesson]).strip() or karma_lesson
                    if col_advice and not pd.isna(row.iloc[0].get(col_advice)):
                        karma_advice = str(row.iloc[0][col_advice]).strip() or karma_advice
    except Exception:
        # Abaikan bila gagal, gunakan default
        pass

    # Prepare Life Path KD object and description from DB (karmic_debt table)
    lpkd = get_karmic_debt(lp, life_path_precursor)
    kd_desc = ''
    try:
        if lpkd and lpkd.get('has_karmic_debt') and lpkd.get('debt_double'):
            fetched = _db_get_karmic_debt_desc(int(lpkd.get('debt_double')))
            if fetched:
                kd_desc = str(fetched).strip()
    except Exception:
        pass
    
    # Prepare Name Number KD object and description from DB
    # Use A1Z26 reduced number for KD detection (not Harani number),
    # BUT only surface Name-based KD when Harani name_number is one of 1,4,5,7.
    name_number_from_a1z26 = name_number_from_a1z26 if 'name_number_from_a1z26' in locals() else 0
    allowed_kd_reduced = {1, 4, 5, 7}
    if name_number in allowed_kd_reduced:
        name_kd = get_karmic_debt(name_number_from_a1z26, name_number_precursor)
    else:
        name_kd = {
            'has_karmic_debt': False,
            'debt_double': None,
            'reduced': name_number_from_a1z26,
            'precursor': name_number_precursor,
        }
    name_kd_desc = ''
    try:
        if name_kd and name_kd.get('has_karmic_debt') and name_kd.get('debt_double'):
            fetched = _db_get_karmic_debt_desc(int(name_kd.get('debt_double')))
            if fetched:
                name_kd_desc = str(fetched).strip()
    except Exception:
        pass

    return {
        # A) Name-based Karma (from missing letters)
        'karma_number': karma_number,
        'name_karma_number': karma_number,
        'karma_description': karma_description,
        'karma_meaning': karma_meaning,
        'karma_lesson': karma_lesson,
        'karma_advice': karma_advice,
        # B) Life Path (from birthdate) and its Karmic Debt detection
        'life_path': lp,
        'life_path_karmic_debt': lpkd,
        'karmic_debt_description': kd_desc,
        # C) Name Number and its Karmic Debt detection
        'name_number': name_number,
        'name_number_karmic_debt': name_kd,
        'name_karmic_debt_description': name_kd_desc,
        # D) Birthdate-based karmic measure (reduced of day+month+year only)
        'birth_karma_number': birth_karma_reduced,
        'birth_karma_karmic_debt': get_karmic_debt(birth_karma_reduced, birth_karma_precursor),
        'calculation': {
            'day': day_v,
            'month': month_v,
            'year': year_v,
            'name_sum': name_sum_raw,
            'total_sum': total_sum,
            'life_path_total_digits': lp_total_digits,
            'life_path_precursor': life_path_precursor,
            'birth_karma_precursor': birth_karma_precursor,
        }
    }

# --- Tenung (nama) calculation ---

def calculate_tenung_name(name: str) -> dict:
    """Hitung angka Tenung dari nama dengan penjumlahan bertetangga.

    Aturan:
    - Huruf A..Z dipetakan ke 1..26 (A1Z26), lalu untuk baris dasar setiap huruf direduksi ke 1..9.
    - Bangun segitiga bilangan: next[i] = reduce_1_9_or_keep_master(cur[i] + cur[i+1]).
    - Nilai 11 dan 22 dipertahankan (tidak direduksi). Selain itu, nilai >9 direduksi ke 1..9.
    - Hasil akhir (elemen tunggal) adalah angka Tenung. Jika bukan 11/22 dan >9, reduksi ke 1..9.

    Keluaran:
    { 'number': int, 'description': str, 'steps': [str] }
    Deskripsi diambil dari tenung_nama.xlsx bila tersedia (kolom fleksibel: no/angka/kode/tenung dan deskripsi/penjelasan/arti/meaning).
    """
    import os
    import pandas as pd

    def reduce_1_9(n: int) -> int:
        n = abs(int(n))
        while n > 9:
            n = sum(int(d) for d in str(n))
        return max(1, n)

    def reduce_1_9_or_keep_master(n: int) -> int:
        if n in (11, 22):
            return n
        return reduce_1_9(n)

    letters = [ch for ch in (name or '') if ch.isalpha()]
    base = []
    steps = []
    for ch in letters:
        val = ord(ch.upper()) - 64  # A1Z26
        base.append(reduce_1_9(val))
    steps.append(f"Base row: {base}")

    if not base:
        return {'number': 0, 'description': 'Nama kosong.', 'steps': steps}

    cur = base[:]
    while len(cur) > 1:
        nxt = []
        for i in range(len(cur) - 1):
            s = cur[i] + cur[i + 1]
            nxt.append(reduce_1_9_or_keep_master(s))
        cur = nxt
        steps.append(f"Next row: {cur}")

    tenung_number = cur[0]
    if tenung_number not in (11, 22) and tenung_number > 9:
        tenung_number = reduce_1_9(tenung_number)

    # Lookup deskripsi Tenung dari database
    description = ''
    try:
        desc = _db_get_tenung_deskripsi(int(tenung_number))
        if desc:
            description = str(desc).strip()
    except Exception:
        pass

    if not description:
        description = f"Penjelasan untuk angka Tenung {tenung_number} tidak tersedia di Excel."

    return {'number': int(tenung_number), 'description': description, 'steps': steps}

# --- Bridge calculation ---

def calculate_bridge(life_path: int, harani_name: int) -> dict:
    """Hitung Bridge Number berdasarkan aturan:
    - bridge_raw = |life_path - harani_name|
    - Jika 5 <= bridge_raw < 8, tampilkan kombinasi angka (life_path dan harani_name)
      sebagai bridge_key (misal "3-5"), jika tidak tampilkan hasil pengurangan (int)
    - Mapping deskripsi diambil dari bridge_number.xlsx.

    Keluaran dict dengan kunci:
    - bridge_number: str | int (kombinasi "x-y" untuk 5..7, atau angka hasil selisih)
    - bridge_description: str (ringkas)
    - bridge_meaning: str
    - bridge_challenge: str
    - bridge_advice: str
    """
    try:
        lp = int(life_path) if life_path is not None else 0
    except Exception:
        lp = 0
    try:
        hn = int(harani_name) if harani_name is not None else 0
    except Exception:
        hn = 0

    # Hitung selisih dengan aturan: angka terbesar dikurangi angka lebih kecil
    bigger = lp if lp >= hn else hn
    smaller = hn if lp >= hn else lp
    diff = bigger - smaller
    # Determine bridge key/value to display
    if 5 <= diff < 8:
        bridge_display = f"{lp}-{hn}"
        combo_norms = [f"{lp}-{hn}", f"{hn}-{lp}", f"{lp}{hn}", f"{hn}{lp}"]
    else:
        bridge_display = diff
        combo_norms = []

    bridge_description = ""
    bridge_meaning = ""
    bridge_challenge = ""
    bridge_advice = ""

    # Primary mapping: bridge_name (bridge -> deskripsi)
    try:
        bn_desc = None
        if combo_norms:
            for key in combo_norms:
                bn_desc = _db_get_bridge_name(key)
                if bn_desc:
                    break
        if not bn_desc:
            bn_desc = _db_get_bridge_name(str(diff))
        if bn_desc:
            bridge_description = str(bn_desc).strip()
    except Exception:
        pass

    # Secondary details: bridge_number (optional), fill remaining fields
    try:
        details = None
        if combo_norms:
            for key in combo_norms:
                details = _db_get_bridge_details(key)
                if details:
                    break
        if not details:
            details = _db_get_bridge_details(str(diff))
        if details:
            if not bridge_description:
                bridge_description = str(details.get('deskripsi', '')).strip()
            bridge_meaning = str(details.get('makna', '')).strip()
            bridge_challenge = str(details.get('tantangan', '')).strip()
            bridge_advice = str(details.get('saran', '')).strip()
    except Exception:
        pass

    return {
        'bridge_number': bridge_display,
        'bridge_description': bridge_description,
        'bridge_meaning': bridge_meaning,
        'bridge_challenge': bridge_challenge,
        'bridge_advice': bridge_advice,
    }


# --- Weton meaning calculation ---

def get_weton_meaning(weton_info: dict) -> str:
    """Get weton meaning based on hari, pasaran, and neptu combination.
    
    Args:
        weton_info: dict containing 'hari', 'pasaran', 'neptu', 'wuku' keys
        
    Returns:
        str: HTML formatted weton meaning description
    """
    try:
        if not weton_info:
            return ""
            
        hari = str(weton_info.get('hari', '')).strip()
        pasaran = str(weton_info.get('pasaran', '')).strip()
        neptu = weton_info.get('neptu', 0)
        wuku = str(weton_info.get('wuku', '')).strip()
        
        if not hari or not pasaran:
            return ""
        
        # Try Excel first
        try:
            import os, pandas as pd
            xlsx_path = os.path.join(os.path.dirname(__file__), 'weton_arti.xlsx')
            if os.path.exists(xlsx_path):
                df = pd.read_excel(xlsx_path)
                if not df.empty and 'Combine' in df.columns:
                    # Build possible keys to handle alias: Umanis == Legi
                    candidates = []
                    # As-is
                    candidates.append(f"{hari}{pasaran}")
                    # Try alias swap between Umanis and Legi
                    if pasaran.lower() == 'umanis':
                        candidates.append(f"{hari}Legi")
                    elif pasaran.lower() == 'legi':
                        candidates.append(f"{hari}Umanis")
                    # Normalize and search
                    df['_norm'] = df['Combine'].astype(str).str.replace(' ', '').str.lower()
                    norm_keys = [c.replace(' ', '').lower() for c in candidates]
                    match = df[df['_norm'].isin(norm_keys)]
                    if not match.empty:
                        row = match.iloc[0]
                        ket_hari = str(row.get('ket_hari', '')).strip() if pd.notna(row.get('ket_hari')) else ''
                        ket_pasaran = str(row.get('ket_pasaran', '')).strip() if pd.notna(row.get('ket_pasaran')) else ''
                        ket_wuku = str(row.get('ket_wuku', '')).strip() if pd.notna(row.get('ket_wuku')) else ''
                        if ket_hari or ket_pasaran or ket_wuku:
                            parts = [f"<p><strong>Weton {hari} {pasaran}</strong> memiliki nilai neptu <strong>{neptu}</strong>.</p>"]
                            if ket_hari: parts.append(f"<p>{ket_hari}</p>")
                            if ket_pasaran: parts.append(f"<p>{ket_pasaran}</p>")
                            # Handle wuku description
                            if wuku:
                                wuku_desc_text = ""
                                if ket_wuku:
                                    wuku_desc_text = ket_wuku
                                else:
                                    # Try to get wuku description from wuku_names.xlsx
                                    try:
                                        wuku_xlsx_path = os.path.join(os.path.dirname(__file__), 'wuku_names.xlsx')
                                        if os.path.exists(wuku_xlsx_path):
                                            wuku_df = pd.read_excel(wuku_xlsx_path)
                                            if not wuku_df.empty and 'wuku' in wuku_df.columns and 'deskripsi' in wuku_df.columns:
                                                wuku_match = wuku_df[wuku_df['wuku'].astype(str).str.strip().str.lower() == wuku.lower()]
                                                if not wuku_match.empty:
                                                    wuku_desc_from_file = str(wuku_match.iloc[0]['deskripsi']).strip()
                                                    if wuku_desc_from_file and not pd.isna(wuku_match.iloc[0]['deskripsi']):
                                                        wuku_desc_text = wuku_desc_from_file
                                    except: pass
                                
                                if wuku_desc_text:
                                    parts.append(f"<p>Wuku <strong>{wuku}</strong>: {wuku_desc_text}</p>")
                                else:
                                    parts.append(f"<p>Wuku <strong>{wuku}</strong> memberikan pengaruh tambahan pada perjalanan hidup dan nasib Anda.</p>")
                            parts.append("<p><em>Ingatlah bahwa weton hanyalah salah satu aspek dalam kehidupan. Yang terpenting adalah bagaimana Anda menjalani hidup dengan baik dan memberikan manfaat bagi sesama.</em></p>")
                            return '\n'.join(parts)
        except: pass
        
        # Create a basic weton meaning based on the combination
        meaning_parts = []
        
        # Add general weton description
        meaning_parts.append(f"<p><strong>Weton {hari} {pasaran}</strong> memiliki nilai neptu <strong>{neptu}</strong>.</p>")
        
        # Add basic interpretation based on neptu value
        if neptu <= 7:
            meaning_parts.append("<p>Neptu rendah menunjukkan kepribadian yang tenang dan bijaksana. Anda cenderung berpikir sebelum bertindak dan memiliki pendekatan yang hati-hati dalam hidup.</p>")
        elif neptu <= 12:
            meaning_parts.append("<p>Neptu sedang menunjukkan keseimbangan dalam kepribadian. Anda memiliki kombinasi yang baik antara ketenangan dan semangat dalam menjalani hidup.</p>")
        else:
            meaning_parts.append("<p>Neptu tinggi menunjukkan kepribadian yang dinamis dan penuh semangat. Anda cenderung aktif dan memiliki energi yang kuat dalam mengejar tujuan.</p>")
        
        # Add day-specific characteristics
        day_meanings = {
            'Minggu': 'memiliki sifat kepemimpinan yang kuat dan karisma alami',
            'Senin': 'memiliki intuisi yang tajam dan kepekaan emosional yang tinggi',
            'Selasa': 'memiliki semangat juang yang tinggi dan keberanian dalam menghadapi tantangan',
            'Rabu': 'memiliki kemampuan komunikasi yang baik dan mudah beradaptasi',
            'Kamis': 'memiliki kebijaksanaan dan kemampuan untuk memberikan nasihat yang baik',
            'Jumat': 'memiliki daya tarik personal yang kuat dan kemampuan bersosialisasi',
            'Sabtu': 'memiliki kedisiplinan tinggi dan kemampuan untuk bekerja keras'
        }
        
        if hari in day_meanings:
            meaning_parts.append(f"<p>Lahir pada hari <strong>{hari}</strong>, Anda {day_meanings[hari]}.</p>")
        
        # Add pasaran-specific characteristics
        pasaran_meanings = {
            'Legi': 'memberikan sifat yang lembut, penyayang, dan mudah bergaul dengan orang lain',
            'Umanis': 'memberikan sifat yang lembut, penyayang, dan mudah bergaul dengan orang lain',  # Alias for Legi
            'Pahing': 'memberikan sifat yang tegas, berani, dan memiliki prinsip yang kuat',
            'Pon': 'memberikan sifat yang kreatif, inovatif, dan memiliki ide-ide cemerlang',
            'Wage': 'memberikan sifat yang stabil, dapat diandalkan, dan memiliki komitmen tinggi',
            'Kliwon': 'memberikan sifat yang spiritual, bijaksana, dan memiliki pemahaman mendalam'
        }
        
        if pasaran in pasaran_meanings:
            meaning_parts.append(f"<p>Pasaran <strong>{pasaran}</strong> {pasaran_meanings[pasaran]}.</p>")
        
        # Add wuku information if available
        if wuku:
            wuku_desc_text = ""
            # Try to get wuku description from wuku_names.xlsx
            try:
                import os
                wuku_xlsx_path = os.path.join(os.path.dirname(__file__), 'wuku_names.xlsx')
                if os.path.exists(wuku_xlsx_path):
                    wuku_df = pd.read_excel(wuku_xlsx_path)
                    if not wuku_df.empty and 'wuku' in wuku_df.columns and 'deskripsi' in wuku_df.columns:
                        wuku_match = wuku_df[wuku_df['wuku'].astype(str).str.strip().str.lower() == wuku.lower()]
                        if not wuku_match.empty:
                            wuku_desc_from_file = str(wuku_match.iloc[0]['deskripsi']).strip()
                            if wuku_desc_from_file and not pd.isna(wuku_match.iloc[0]['deskripsi']):
                                wuku_desc_text = wuku_desc_from_file
            except: pass
            
            if wuku_desc_text:
                meaning_parts.append(f"<p>Wuku <strong>{wuku}</strong>: {wuku_desc_text}</p>")
            else:
                meaning_parts.append(f"<p>Wuku <strong>{wuku}</strong> memberikan pengaruh tambahan pada perjalanan hidup dan nasib Anda.</p>")
        
        # Add general advice
        meaning_parts.append("<p><em>Ingatlah bahwa weton hanyalah salah satu aspek dalam kehidupan. Yang terpenting adalah bagaimana Anda menjalani hidup dengan baik dan memberikan manfaat bagi sesama.</em></p>")
        
        return '\n'.join(meaning_parts)
        
    except Exception as e:
        # Return a simple fallback message if anything goes wrong
        return f"<p>Weton Anda memiliki karakteristik unik berdasarkan kombinasi hari dan pasaran kelahiran.</p>"
def get_karmic_debt(reduced, precursor):
    """Determine Karmic Debt presence from a reduced single digit and its two-digit precursor.

    Rules:
    - Karmic Debt doubles: 13→4, 14→5, 16→7, 19→1
{{ ... }}

    Args:
        reduced: Final single digit (e.g., 1, 4, 5, 7). Accepts int or str.
        precursor: Two-digit source before reduction (e.g., 19, 13, 14, 16). Accepts int or str.

    Returns:
        dict with keys:
          - has_karmic_debt (bool)
          - debt_double (int | None)  # 13, 14, 16, or 19 when present
          - reduced (int | None)
          - precursor (int | None)
    """
    # Mapping of Karmic Debt doubles to their reduced single-digit targets
    kd_map = {13: 4, 14: 5, 16: 7, 19: 1}

    try:
        r = int(reduced) if reduced is not None else None
        p = int(precursor) if precursor is not None else None
    except Exception:
        return {
            'has_karmic_debt': False,
            'debt_double': None,
            'reduced': reduced,
            'precursor': precursor,
        }

    debt = p if (p in kd_map and kd_map[p] == r) else None
    return {
        'has_karmic_debt': bool(debt),
        'debt_double': debt,
        'reduced': r,
        'precursor': p,
    }


def papan_pythagoras_calculation(name):
    """
    Calculate Papan Pythagoras (Pythagorean Chart) based on name.
    
    Distributes letter values into 9 boxes:
    - Row 1 (Mind): 3, 6, 9
    - Row 2 (Soul): 2, 5, 8  
    - Row 3 (Body): 1, 4, 7
    
    - Column 1 (Self): 1, 2, 3
    - Column 2 (Community): 4, 5, 6
    - Column 3 (World): 7, 8, 9
    
    Args:
        name (str): Full name to analyze
        
    Returns:
        dict: Papan Pythagoras data with counts and descriptions
    """
    try:
        if not name or not isinstance(name, str):
            return {'error': 'Invalid name provided'}
        
        # A1Z26 mapping (Pythagorean system)
        letter_values = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
            'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
            'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
        }
        
        # Initialize counts for each number 1-9
        counts = {i: 0 for i in range(1, 10)}
        
        # Count occurrences of each number from name
        clean_name = name.upper().replace(' ', '')
        for letter in clean_name:
            if letter in letter_values:
                value = letter_values[letter]
                counts[value] += 1
        
        # Map to Pythagorean Chart positions
        chart = {
            # Row 1 - Mind
            'mind_self': counts[3],      # Position 3
            'mind_community': counts[6], # Position 6
            'mind_world': counts[9],     # Position 9
            
            # Row 2 - Soul
            'soul_self': counts[2],      # Position 2
            'soul_community': counts[5], # Position 5
            'soul_world': counts[8],     # Position 8
            
            # Row 3 - Body
            'body_self': counts[1],      # Position 1
            'body_community': counts[4], # Position 4
            'body_world': counts[7],     # Position 7
        }
        
        # Calculate totals for rows and columns
        totals = {
            'mind_total': counts[3] + counts[6] + counts[9],
            'soul_total': counts[2] + counts[5] + counts[8],
            'body_total': counts[1] + counts[4] + counts[7],
            'self_total': counts[1] + counts[2] + counts[3],
            'community_total': counts[4] + counts[5] + counts[6],
            'world_total': counts[7] + counts[8] + counts[9]
        }
        
        # Get descriptions from database using the existing format
        descriptions = {}
        position_map = {
            'mind_self': 3,      # Position 3
            'mind_community': 6, # Position 6  
            'mind_world': 9,     # Position 9
            'soul_self': 2,      # Position 2
            'soul_community': 5, # Position 5
            'soul_world': 8,     # Position 8
            'body_self': 1,      # Position 1
            'body_community': 4, # Position 4
            'body_world': 7,     # Position 7
        }
        
        for position, count in chart.items():
            position_num = position_map.get(position)
            if position_num and count > 0:
                # Create database key based on count pattern
                if count == 1:
                    db_key = str(position_num)
                else:
                    db_key = str(position_num) * count  # Repeat digit for count
                
                from db_access import get_papan_pythagoras_desc
                descriptions[position] = get_papan_pythagoras_desc(db_key)
            else:
                # For count = 0, use special key
                from db_access import get_papan_pythagoras_desc
                descriptions[position] = get_papan_pythagoras_desc('0')
        
        # Detect isolated numbers
        isolated_numbers = detect_isolated_numbers(counts)
        
        # Detect sequential patterns
        sequential_patterns = detect_sequential_patterns(counts)
        
        return {
            'name': name,
            'chart': chart,
            'totals': totals,
            'raw_counts': counts,
            'descriptions': descriptions,
            'isolated_numbers': isolated_numbers,
            'sequential_patterns': sequential_patterns,
            'letter_breakdown': {letter: letter_values.get(letter, 0) for letter in clean_name if letter in letter_values}
        }
        
    except Exception as e:
        print(f"Error in papan_pythagoras_calculation: {e}")
        return {'error': f'Calculation error: {str(e)}'}


def birth_chart_calculation(birth_date: str) -> dict:
    """Build a Birth Chart (3x3) from birth date digits.

    Counting rules:
    - Take digits from DDMMYYYY.
    - Count occurrences for numbers 1..9 (ignore 0).

    Grid mapping:
    - Row 1 Mind Plane (Mental/Thinking): positions 3,6,9 -> keys mind_self, mind_community, mind_world
    - Row 2 Soul Plane (Spiritual/Feeling): positions 2,5,8 -> keys soul_self, soul_community, soul_world
    - Row 3 Basic Self (Practical/Doing): positions 1,4,7 -> keys body_self, body_community, body_world

    Returns chart counts, totals, and DB-driven descriptions per box.
    """
    from datetime import datetime
    try:
        # Parse date to components
        dt = None
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y'):
            try:
                dt = datetime.strptime((birth_date or '').strip(), fmt)
                break
            except Exception:
                continue
        if not dt:
            return {'error': 'Invalid birth date'}

        digits = dt.strftime('%d%m%Y')
        # Count occurrences of 1..9
        counts = {i: 0 for i in range(1, 10)}
        for ch in digits:
            if ch.isdigit():
                v = int(ch)
                if 1 <= v <= 9:
                    counts[v] += 1

        chart = {
            # Mind (3,6,9)
            'mind_self': counts[3],
            'mind_community': counts[6],
            'mind_world': counts[9],
            # Soul (2,5,8)
            'soul_self': counts[2],
            'soul_community': counts[5],
            'soul_world': counts[8],
            # Body (1,4,7)
            'body_self': counts[1],
            'body_community': counts[4],
            'body_world': counts[7],
        }

        # Build string representations per cell (repeat the digit N times)
        strings = {
            'mind_self_str': '3' * counts[3],
            'mind_community_str': '6' * counts[6],
            'mind_world_str': '9' * counts[9],
            'soul_self_str': '2' * counts[2],
            'soul_community_str': '5' * counts[5],
            'soul_world_str': '8' * counts[8],
            'body_self_str': '1' * counts[1],
            'body_community_str': '4' * counts[4],
            'body_world_str': '7' * counts[7],
        }

        totals = {
            'mind_total': counts[3] + counts[6] + counts[9],
            'soul_total': counts[2] + counts[5] + counts[8],
            'body_total': counts[1] + counts[4] + counts[7],
            'self_total': counts[1] + counts[2] + counts[3],
            'community_total': counts[4] + counts[5] + counts[6],
            'world_total': counts[7] + counts[8] + counts[9],
        }

        # Fetch descriptions per position_count from DB
        position_order = [
            ('mind_self', 3), ('mind_community', 6), ('mind_world', 9),
            ('soul_self', 2), ('soul_community', 5), ('soul_world', 8),
            ('body_self', 1), ('body_community', 4), ('body_world', 7),
        ]
        descriptions = {}
        from db_access import get_birth_chart_desc
        for key, pos_num in position_order:
            cnt = chart[key]
            desc_key = f"{key}_{cnt}"
            descriptions[key] = get_birth_chart_desc(desc_key)

        return {
            'birth_date': dt.strftime('%d/%m/%Y'),
            'chart': chart,
            'totals': totals,
            'raw_counts': counts,
            'strings': strings,
            'descriptions': descriptions,
        }
    except Exception as e:
        return {'error': f'Calculation error: {e}'}

def detect_arrows_from_birth_date(birth_date: str) -> dict:
    """Detect arrow patterns based on presence/absence of digits in the 3x3 birth chart.

    Presence means the digit exists at least once in the birth date (count > 0).
    Rules implemented (present):
    - arrow_determination: 1,5,9 present
    - arrow_spirituality: 3,5,7 present
    - arrow_intellect: 3,6,9 present
    - arrow_emotional_balance: 2,5,8 present
    - arrow_practicality: 1,4,7 present
    - arrow_planner: 1,2,3 present
    - arrow_will: 4,5,6 present
    - arrow_activity: 7,8,9 present

    Absence counterparts (all three absent):
    - arrow_procrastination: 1,5,9 absent
    - arrow_enquirer: 3,5,7 absent
    - arrow_poor_memory: 3,6,9 absent
    - arrow_hypersensitivity: 2,5,8 absent
    - arrow_disorder: 1,4,7 absent
    - arrow_frustration: 4,5,6 absent
    - arrow_passivity: 7,8,9 absent

    If none of the present-arrows matched, include 'arrow_no_arrows'.
    """
    bc = birth_chart_calculation(birth_date)
    if bc.get('error'):
        return {'error': bc['error']}

    counts = bc.get('raw_counts', {})
    def present(*digits):
        return all(counts.get(d, 0) > 0 for d in digits)
    def absent(*digits):
        return all(counts.get(d, 0) == 0 for d in digits)

    arrows_present = []
    arrows_absent = []

    # Present arrows
    if present(1,5,9): arrows_present.append('arrow_determination')
    if present(3,5,7): arrows_present.append('arrow_spirituality')
    if present(3,6,9): arrows_present.append('arrow_intellect')
    if present(2,5,8): arrows_present.append('arrow_emotional_balance')
    if present(1,4,7): arrows_present.append('arrow_practicality')
    if present(1,2,3): arrows_present.append('arrow_planner')
    if present(4,5,6): arrows_present.append('arrow_will')
    if present(7,8,9): arrows_present.append('arrow_activity')

    # Absence arrows
    if absent(1,5,9): arrows_absent.append('arrow_procrastination')
    if absent(3,5,7): arrows_absent.append('arrow_enquirer')
    if absent(3,6,9): arrows_absent.append('arrow_poor_memory')
    if absent(2,5,8): arrows_absent.append('arrow_hypersensitivity')
    if absent(1,4,7): arrows_absent.append('arrow_disorder')
    if absent(4,5,6): arrows_absent.append('arrow_frustration')
    if absent(7,8,9): arrows_absent.append('arrow_passivity')

    # Compute presence counts for rows (Mind/Soul/Body) and columns (Self/Community/World)
    lines = {
        # Rows by planes
        'row_mind': (3,6,9),
        'row_soul': (2,5,8),
        'row_body': (1,4,7),
        # Columns by focus
        'col_self': (1,2,3),
        'col_community': (4,5,6),
        'col_world': (7,8,9),
    }
    line_presence = {}
    for key, triple in lines.items():
        line_presence[key] = sum(1 for d in triple if counts.get(d, 0) > 0)

    # "Birth Charts With No Arrows": hanya jika TIDAK ada panah hadir maupun panah absen
    # dan setiap baris & kolom berisi tepat 1 atau 2 (bukan 0 atau 3). Ini mencegah kontradiksi
    # ketika diagonal atau garis lain terdeteksi sebagai panah.
    no_arrows_rows_cols = all(v in (1,2) for v in line_presence.values())
    if no_arrows_rows_cols and not arrows_present and not arrows_absent:
        arrows_present.append('arrow_no_arrows')

    return {
        'arrows_present': arrows_present,
        'arrows_absent': arrows_absent,
        'birth_chart': bc.get('chart'),
        'strings': bc.get('strings'),
        'totals': bc.get('totals'),
        'line_presence': line_presence,
    }

def detect_isolated_numbers(counts):
    """
    Detect isolated numbers in Pythagorean chart.
    
    Isolation rules:
    
- Number 1 is isolated if positions 2, 4, and 5 are empty
    - Number 3 is isolated if positions 2, 5, and 6 are empty  
    - Number 7 is isolated if positions 4, 5, and 8 are empty
    - Number 9 is isolated if positions 5, 6, and 8 are empty
    
    Args:
{{ ... }}
        counts (dict): Dictionary with counts for each position 1-9
        
    Returns:
        dict: Information about isolated numbers with descriptions
    """
    try:
        isolated = []
        
        # Check isolation for number 1 (surrounded by 2, 4, 5)
        if counts[1] > 0 and counts[2] == 0 and counts[4] == 0 and counts[5] == 0:
            from db_access import get_angka_terisolasi_desc
            isolated.append({
                'number': 1,
                'count': counts[1],
                'description': get_angka_terisolasi_desc(1)
            })
        
        # Check isolation for number 3 (surrounded by 2, 5, 6)
        if counts[3] > 0 and counts[2] == 0 and counts[5] == 0 and counts[6] == 0:
            from db_access import get_angka_terisolasi_desc
            isolated.append({
                'number': 3,
                'count': counts[3],
                'description': get_angka_terisolasi_desc(3)
            })
        
        # Check isolation for number 7 (surrounded by 4, 5, 8)
        if counts[7] > 0 and counts[4] == 0 and counts[5] == 0 and counts[8] == 0:
            from db_access import get_angka_terisolasi_desc
            isolated.append({
                'number': 7,
                'count': counts[7],
                'description': get_angka_terisolasi_desc(7)
            })
        
        # Check isolation for number 9 (surrounded by 5, 6, 8)
        if counts[9] > 0 and counts[5] == 0 and counts[6] == 0 and counts[8] == 0:
            from db_access import get_angka_terisolasi_desc
            isolated.append({
                'number': 9,
                'count': counts[9],
                'description': get_angka_terisolasi_desc(9)
            })
        
        return {
            'has_isolated': len(isolated) > 0,
            'isolated_list': isolated,
            'total_isolated': len(isolated)
        }
        
    except Exception as e:
        print(f"Error in detect_isolated_numbers: {e}")
        return {
            'has_isolated': False,
            'isolated_list': [],
            'total_isolated': 0
        }


def detect_sequential_patterns(counts):
    """
    Detect sequential number patterns in Pythagorean chart.
    
    Patterns to detect:
    - Diagonal 1-5-9: positions 1, 5, 9
    - Diagonal 3-5-7: positions 3, 5, 7
    - Row Body (1-4-7): positions 1, 4, 7
    - Row Soul (2-5-8): positions 2, 5, 8
    - Row Mind (3-6-9): positions 3, 6, 9
    - Column Self (1-2-3): positions 1, 2, 3
    - Column Community (4-5-6): positions 4, 5, 6
    - Column World (7-8-9): positions 7, 8, 9
    
    Args:
        counts (dict): Dictionary with counts for each position 1-9
        
    Returns:
        dict: Information about sequential patterns with descriptions
    """
    try:
        patterns = []
        
        # Define pattern checks
        pattern_checks = [
            # Diagonals
            {
                'id': 'diagonal_159',
                'name': 'Diagonal 1-5-9',
                'positions': [1, 5, 9],
                'expected_values': [1, 5, 9]
            },
            {
                'id': 'diagonal_357',
                'name': 'Diagonal 3-5-7',
                'positions': [3, 5, 7],
                'expected_values': [3, 5, 7]
            },
            # Rows
            {
                'id': 'baris_body',
                'name': 'Baris Body (1-4-7)',
                'positions': [1, 4, 7],
                'expected_values': [1, 4, 7]
            },
            {
                'id': 'baris_soul',
                'name': 'Baris Soul (2-5-8)',
                'positions': [2, 5, 8],
                'expected_values': [2, 5, 8]
            },
            {
                'id': 'baris_mind',
                'name': 'Baris Mind (3-6-9)',
                'positions': [3, 6, 9],
                'expected_values': [3, 6, 9]
            },
            # Columns
            {
                'id': 'kolom_self',
                'name': 'Kolom Self (1-2-3)',
                'positions': [1, 2, 3],
                'expected_values': [1, 2, 3]
            },
            {
                'id': 'kolom_community',
                'name': 'Kolom Community (4-5-6)',
                'positions': [4, 5, 6],
                'expected_values': [4, 5, 6]
            },
            {
                'id': 'kolom_world',
                'name': 'Kolom World (7-8-9)',
                'positions': [7, 8, 9],
                'expected_values': [7, 8, 9]
            }
        ]
        
        for pattern in pattern_checks:
            # Check if all positions have their expected values (deret)
            # BERDERET = nilai di posisi sama dengan nomor posisi
            # Contoh: posisi 1,5,9 -> nilai harus 1,5,9 (atau lebih)
            has_sequential_values = all(counts[pos] >= pos for pos in pattern['positions'])
            
            # Check if all positions are empty (tanpa)
            all_empty = all(counts[pos] == 0 for pos in pattern['positions'])
            
            if has_sequential_values and not all_empty:
                from db_access import get_angka_berderet_desc
                patterns.append({
                    'id': pattern['id'],
                    'name': pattern['name'],
                    'status': 'deret',
                    'positions': pattern['positions'],
                    'values': [counts[pos] for pos in pattern['positions']],
                    'description': get_angka_berderet_desc(pattern['id'], 'deret')
                })
            elif all_empty:
                from db_access import get_angka_berderet_desc
                patterns.append({
                    'id': pattern['id'],
                    'name': pattern['name'],
                    'status': 'tanpa',
                    'positions': pattern['positions'],
                    'values': [counts[pos] for pos in pattern['positions']],
                    'description': get_angka_berderet_desc(pattern['id'], 'tanpa')
                })
        
        return {
            'has_patterns': len(patterns) > 0,
            'patterns_list': patterns,
            'total_patterns': len(patterns)
        }
        
    except Exception as e:
        print(f"Error in detect_sequential_patterns: {e}")
        return {
            'has_patterns': False,
            'patterns_list': [],
            'total_patterns': 0
        }


def chaldean_calculation(name: str) -> dict:
    """
    Calculate Chaldean numerology using neighbor sum method.
    
    Chaldean alphabet values:
    A=1, B=2, C=3, D=4, E=5, F=8, G=3, H=5, I=1, J=1, K=2, L=3, M=4, N=5, O=7, P=8, Q=1, R=2, S=3, T=4, U=6, V=6, W=6, X=5, Y=1, Z=7
    
    Args:
        name (str): Name to calculate
        
    Returns:
        dict: Chaldean calculation result with number and description
    """
    try:
        # Chaldean alphabet mapping
        chaldean_values = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 8, 'G': 3, 'H': 5, 'I': 1,
            'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 7, 'P': 8, 'Q': 1, 'R': 2,
            'S': 3, 'T': 4, 'U': 6, 'V': 6, 'W': 6, 'X': 5, 'Y': 1, 'Z': 7
        }
        
        def reduce_to_single_digit(n: int) -> int:
            """Reduce number to single digit (1-9)."""
            n = abs(int(n))
            if n == 0:
                return 0
            while n > 9:
                n = sum(int(d) for d in str(n))
            return n
        
        # Extract letters and convert to Chaldean values
        letters = [ch.upper() for ch in (name or '') if ch.isalpha()]
        if not letters:
            return {'number': 0, 'description': 'Nama tidak valid', 'steps': []}
        
        base_values = [chaldean_values.get(ch, 0) for ch in letters]
        
        # Build calculation steps for transparency
        steps = []
        steps.append(f"Nama: {name}")
        steps.append(f"Huruf: {' '.join(letters)}")
        steps.append(f"Nilai Chaldean: {' '.join(map(str, base_values))}")
        
        # Neighbor sum method (bertetangga)
        current = base_values[:]
        step_num = 1
        
        while len(current) > 1:
            next_row = []
            for i in range(len(current) - 1):
                neighbor_sum = current[i] + current[i + 1]
                reduced = reduce_to_single_digit(neighbor_sum)
                next_row.append(reduced)
            
            steps.append(f"Langkah {step_num}: {' '.join(map(str, next_row))}")
            current = next_row
            step_num += 1
        
        final_number = current[0] if current else 0
        
        # Get description from database
        from db_access import get_chaldean_desc
        description = get_chaldean_desc(final_number)
        
        return {
            'number': final_number,
            'description': description,
            'steps': steps,
            'letter_values': dict(zip(letters, base_values))
        }
        
    except Exception as e:
        print(f"Error in chaldean_calculation: {e}")
        return {
            'number': 0,
            'description': 'Terjadi kesalahan dalam perhitungan',
            'steps': [],
            'letter_values': {}
        }
