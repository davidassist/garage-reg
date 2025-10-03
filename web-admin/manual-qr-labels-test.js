/**
 * QR Címkék Manuális Teszt Útmutató
 * 
 * A QR címke tömeges nyomtatás és gyári QR funkciók tesztelése
 */

console.log('🏷️ QR Címkék Manuális Teszt Útmutató')
console.log('=====================================')

console.log('\n📋 Teszt Esetek:')

console.log('\n1️⃣ TÖMEGES CÍMKE GENERÁLÁS TESZT')
console.log('--------------------------------')
console.log('Lépések:')
console.log('1. Nyissa meg: http://localhost:3000/gates')
console.log('2. Jelöljön ki 3-5 kaput checkbox-szal')
console.log('3. Kattintson "Tömeges címke" gombra')
console.log('4. Válassza ki szűrő típusát: "Kiválasztott kapuk"')
console.log('5. Állítsa be: A4 papír, 3 oszlop, 9 címke/oldal')
console.log('6. Jelölje be: QR kód ✓, Kapu információk ✓')
console.log('7. Kattintson "Előnézet" gombra')
console.log('8. Ellenőrizze a címkék kinézetét')
console.log('9. Kattintson "PDF letöltés" gombra')
console.log('')
console.log('Elvárás:')
console.log('✅ PDF fájl letöltődik')
console.log('✅ Címkék tartalmaznak QR kódot és kapu adatokat') 
console.log('✅ 3 oszlopos elrendezés')
console.log('✅ Információs táblázat a végén')

console.log('\n2️⃣ ÉPÜLET/TELEPHELY SZŰRÉS TESZT')
console.log('-------------------------------')
console.log('Lépések:')
console.log('1. Nyissa meg: http://localhost:3000/gates')
console.log('2. Kattintson "Tömeges címke" gombra')
console.log('3. Válassza "Épület szerint" szűrőt')
console.log('4. Válasszon egy épületet a dropdown-ból')
console.log('5. Ellenőrizze a "X kapu lesz címkézve" üzenetet')
console.log('6. Generálja le a PDF-et')
console.log('')
console.log('Elvárás:')
console.log('✅ Csak a kiválasztott épület kapui szerepelnek')
console.log('✅ Kapu szám helyesen jelenik meg')
console.log('✅ PDF tartalmazza az épület összes kapuját')

console.log('\n3️⃣ GYÁRI QR MAPPING GENERÁLÁS TESZT')
console.log('----------------------------------')
console.log('Lépések:')
console.log('1. Nyissa meg: http://localhost:3000/gates')
console.log('2. Kattintson "Gyári QR" gombra') 
console.log('3. A "Gyári QR mapping generálás" szekcióban:')
console.log('   - Kapuk száma: 50')
console.log('   - Batch név: "test_batch_2024"')
console.log('4. Kattintson "CSV letöltés" gombra')
console.log('5. Nyissa meg a letöltött CSV fájlt')
console.log('')
console.log('Elvárás:')
console.log('✅ CSV fájl letöltődik: factory_qr_mapping_50.csv')
console.log('✅ Fejléc: gate_code,factory_qr,batch,generated_at')
console.log('✅ 50 sor kapu adattal')
console.log('✅ FQR- prefix a QR tokenekben')
console.log('✅ Batch név: test_batch_2024')
console.log('✅ ISO időbélyegek')

console.log('\n4️⃣ GYÁRI QR CSV IMPORT TESZT')
console.log('----------------------------')
console.log('Lépések:')
console.log('1. Hozzon létre test.csv fájlt:')
console.log('   gate_id,factory_qr')
console.log('   1,FQR-test-abc123')
console.log('   2,FQR-test-def456')
console.log('   999,FQR-test-invalid')
console.log('2. Nyissa meg: http://localhost:3000/gates')
console.log('3. Kattintson "Gyári QR" gombra')
console.log('4. A "Gyári QR CSV import" szekcióban:')
console.log('   - Válassza ki a test.csv fájlt')
console.log('   - Batch név: "manual_test_import"')
console.log('5. Kattintson "CSV importálása" gombra')
console.log('6. Ellenőrizze az import eredményeket')
console.log('')
console.log('Elvárás:')
console.log('✅ Import eredmény: 2 sikeres, 1 hiba')
console.log('✅ Hiba üzenet: "Kapu nem található: 999"')
console.log('✅ Batch név helyesen megjelenik')
console.log('✅ Toast notification sikeres importról')

console.log('\n5️⃣ MINTA ELŐNÉZET TESZT')
console.log('-----------------------')
console.log('Lépések:')
console.log('1. Nyissa meg: http://localhost:3000/gates')
console.log('2. Jelöljön ki 6 kaput')
console.log('3. Kattintson "Minta előnézet" gombra')
console.log('4. Ellenőrizze a címkék elrendezését')
console.log('5. Próbálja ki a "Nyomtatás" funkciót (Ctrl+P)')
console.log('6. Tekintse át az információs táblázatot')
console.log('')
console.log('Elvárás:')
console.log('✅ 6 címke 3x2 elrendezésben')
console.log('✅ QR kód placeholder minden címkén')
console.log('✅ Kapu név, épület, sorozatszám látható')
console.log('✅ Nyomtatási nézet optimalizált')
console.log('✅ Információs táblázat QR URL-ekkel')

console.log('\n6️⃣ SZÉLSŐSÉGES ESETEK TESZTJE')
console.log('----------------------------')
console.log('Lépések:')
console.log('1. Próbálja címke generálást 0 kiválasztott kapuval')
console.log('2. Töltse fel nem CSV fájlt a gyári QR importnál')
console.log('3. Hagyja üresen a batch nevet')
console.log('4. Állítson be 100 címke/oldal értéket')
console.log('5. Generáljon 10000 kapus mappinget')
console.log('')
console.log('Elvárás:')
console.log('✅ "PDF letöltés" gomb letiltva 0 kapu esetén')
console.log('✅ "Csak CSV fájlok támogatottak" hibaüzenet')
console.log('✅ "CSV importálása" gomb letiltva üres batch név esetén')
console.log('✅ Címke/oldal érték 20-ra korlátozva')
console.log('✅ Mapping generálás működik nagy mennyiségnél')

console.log('\n7️⃣ RESPONSIVE DESIGN TESZT')
console.log('--------------------------')
console.log('Lépések:')
console.log('1. Tesztelje mobilon (375px szélesség)')
console.log('2. Nyissa meg a címke generáló dialógust')
console.log('3. Próbálja ki a gyári QR dialógust')
console.log('4. Ellenőrizze a gombok elrendezését')
console.log('')
console.log('Elvárás:')
console.log('✅ Dialógusok responsive módon jelennek meg')
console.log('✅ Gombok nem takarják el egymást')
console.log('✅ Form elemek használhatók mobilon')
console.log('✅ Scroll működik szűk képernyőn')

console.log('\n8️⃣ TELJESÍTMÉNY TESZT')
console.log('--------------------')
console.log('Lépések:')
console.log('1. Jelöljön ki 50+ kaput')
console.log('2. Generáljon PDF-et')
console.log('3. Mérje a generálási időt')
console.log('4. Ellenőrizze a memóriahasználatot')
console.log('5. Töltse fel 1MB-os CSV fájlt')
console.log('')
console.log('Elvárás:')
console.log('✅ PDF generálás <10 másodperc')
console.log('✅ Nincs memória túlcsordulás')
console.log('✅ Progress indikátor működik')
console.log('✅ Nagy CSV fájlok kezelhetők')

console.log('\n📊 TESZT EREDMÉNYEK ELLENŐRZÉSI LISTA')
console.log('====================================')

const testResults = [
  '□ Tömeges címke PDF generálás működik',
  '□ Épület/telephely szűrés helyes', 
  '□ Gyári QR mapping CSV generálás',
  '□ Gyári QR CSV import hibakezeléssel',
  '□ Minta előnézet és nyomtatás',
  '□ Hibakezelés szélsőséges esetekben',
  '□ Responsive design mobilon',
  '□ Teljesítmény elvárásoknak megfelelő',
  '□ RBAC jogosultságok ellenőrizve',
  '□ API végpontok válaszolnak'
]

testResults.forEach((result, index) => {
  console.log(`${index + 1}. ${result}`)
})

console.log('\n🎯 ELFOGADÁSI KRITÉRIUMOK')
console.log('========================')
console.log('✅ Admin oldalon kiválasztott kapukhoz összevont PDF címkelap')
console.log('✅ Import „factory QR" CSV (kapu azonosítás előre gyártott tokennel)')
console.log('✅ Mintalap generálás működik')
console.log('✅ Gyári QR mapping CSV letöltés')

console.log('\n📝 TESZT JEGYZET SABLON')
console.log('======================')
console.log('Tesztelő: _______________')
console.log('Dátum: _______________')
console.log('Böngésző: _______________')
console.log('Képernyő felbontás: _______________')
console.log('')
console.log('Talált hibák:')
console.log('1. _________________________________')
console.log('2. _________________________________')
console.log('3. _________________________________')
console.log('')
console.log('Javaslatok:')
console.log('1. _________________________________')
console.log('2. _________________________________')
console.log('3. _________________________________')

console.log('\n✅ TESZT BEFEJEZVE')
console.log('Minden teszt eset lefutott? Töltse ki a jegyzetet!')
console.log('Hibák esetén készítsen screenshot-okat és részletes leírást.')

// CSV fájl generálása teszteléshez
function generateTestCSV() {
  const csvContent = `gate_id,factory_qr
1,FQR-test-abc123def
2,FQR-test-def456ghi
3,FQR-test-ghi789jkl
999,FQR-test-invalid
GATE-001,FQR-test-mno012pqr`

  console.log('\n📄 TESZT CSV TARTALOM:')
  console.log('Mentse el "test.csv" néven:')
  console.log('--------------------------------')
  console.log(csvContent)
  console.log('--------------------------------')
}

generateTestCSV()

console.log('\nSikeres tesztelést! 🎉')