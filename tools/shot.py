import sys
from playwright.sync_api import sync_playwright
URL = 'http://127.0.0.1:8501'
OUT = '/w/results/figures/demo'
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1000, 'height': 1150}, device_scale_factor=1.5)
    pg.goto(URL); pg.wait_for_selector('text=Tự động phát hiện', timeout=60000); pg.wait_for_timeout(2500)
    pg.screenshot(path=f'{OUT}/ui_intro.png', full_page=False)
    # trang giảng viên, bài smallest
    pg.locator('label[data-baseweb="radio"]').filter(has_text='② Dành cho giảng viên').click(); pg.wait_for_timeout(2000)
    pg.locator('div[data-testid="stSelectbox"]').first.click(); pg.wait_for_timeout(500)
    pg.get_by_role('option', name='Tìm số nhỏ nhất (smallest)').click(); pg.wait_for_timeout(2500)
    pg.locator('summary').filter(has_text='C0 · So sánh nghiêm ngặt').click(); pg.wait_for_timeout(1500)
    pg.get_by_text('Các lỗi phổ biến').first.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    pg.get_by_text('Các lỗi phổ biến').first.evaluate('e => e.scrollIntoView({block: "start"})'); pg.wait_for_timeout(1000)
    pg.screenshot(path=f'{OUT}/ui_teacher.png')
    # trang nộp bài
    pg.locator('label[data-baseweb="radio"]').filter(has_text='③ Thử nộp bài').click(); pg.wait_for_timeout(2000)
    sb = pg.locator('div[data-testid="stSelectbox"]')
    sb.nth(0).click(); pg.wait_for_timeout(500); pg.get_by_role('option', name='Tìm số nhỏ nhất (smallest)').click(); pg.wait_for_timeout(2000)
    sb.nth(1).click(); pg.wait_for_timeout(500); pg.get_by_role('option', name='Bài tự viết — smallest_so_sanh_nghiem_ngat').click(); pg.wait_for_timeout(2000)
    pg.get_by_role('button', name='Chấm và chẩn đoán').click()
    pg.wait_for_selector('text=Chẩn đoán:', timeout=120000); pg.wait_for_timeout(2500)
    pg.get_by_text('Bài trượt', exact=False).first.evaluate('e => e.scrollIntoView({block: "start"})'); pg.wait_for_timeout(1200)
    pg.screenshot(path=f'{OUT}/ui_submit.png')
    pg.get_by_text('Đề bài: Tìm số nhỏ nhất').first.scroll_into_view_if_needed(); pg.wait_for_timeout(800)
    pg.screenshot(path=f'{OUT}/ui_problem.png')
    b.close()
print('ok')
