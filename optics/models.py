from optics import db

class Common(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spoolID = db.Column(db.String(13), unique=True, nullable=False, index=True)
    create_date = db.Column(db.DateTime(), nullable=False)
    measure_date = db.Column(db.Date(), nullable=False)
    measure_batchNumber = db.Column(db.String(8), nullable=False)
    info = db.Column(db.String(23), nullable=False)
    preform = db.Column(db.String(8), nullable=False)
    ncrCode1 = db.Column(db.String(2), nullable=True)
    ncrCode2 = db.Column(db.String(2), nullable=True)
    ncrCode3 = db.Column(db.String(2), nullable=True)
    resin = db.Column(db.String(1), nullable=False)
    drawNumber = db.Column(db.String(2), nullable=False)
    ptNumber = db.Column(db.String(2), nullable=False)
    com = db.Column(db.String(2), nullable=False)
    rework = db.Column(db.String(1), nullable=False)
    productType = db.Column(db.String(2), nullable=True)
    coat200 = db.Column(db.String(1), nullable=True)

class Packing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime(), nullable=False)
    customerName = db.Column(db.String(20), nullable=False)
    stdLength = db.Column(db.REAL)
    orderLength = db.Column(db.REAL, nullable=False)
    packedLength = db.Column(db.REAL, nullable=False)
    packedSpoolCount = db.Column(db.Integer, nullable=False)

class OTDR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    common_id = db.Column(db.Integer, nullable=False)
    spoolID = db.Column(db.String(13), unique=True, nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    length = db.Column(db.Integer, nullable=False)

    att1310ise = db.Column(db.REAL, nullable=True)
    att1310ose = db.Column(db.REAL, nullable=True)
    att1550ise = db.Column(db.REAL, nullable=True)
    att1550ose = db.Column(db.REAL, nullable=True)
    att1383ise = db.Column(db.REAL, nullable=True)
    att1383ose = db.Column(db.REAL, nullable=True)
    att1625ise = db.Column(db.REAL, nullable=True)
    att1625ose = db.Column(db.REAL, nullable=True)

class MFD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    common_id = db.Column(db.Integer, nullable=False)
    spoolID = db.Column(db.String(13), unique=True, nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    mfd1310ise = db.Column(db.REAL, nullable=True)
    mfd1310ose = db.Column(db.REAL, nullable=True)
    mfd1550ise = db.Column(db.REAL, nullable=True)
    mfd1550ose = db.Column(db.REAL, nullable=True)

class Cutoff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    common_id = db.Column(db.Integer, nullable=False)
    spoolID = db.Column(db.String(13), unique=True, nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    fiberCutoffIse = db.Column(db.REAL, nullable=True)
    fiberCutoffOse = db.Column(db.REAL, nullable=True)
    cableCutoff = db.Column(db.REAL, nullable=True)

class Geometry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    common_id = db.Column(db.Integer, nullable=False)
    spoolID = db.Column(db.String(13), unique=True, nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    cladDiaIse = db.Column(db.REAL, nullable=True)
    cladDiaOse = db.Column(db.REAL, nullable=True)
    cladOvoIse = db.Column(db.REAL, nullable=True)
    cladOvoOse = db.Column(db.REAL, nullable=True)
    eccIse = db.Column(db.REAL, nullable=True)
    eccOse = db.Column(db.REAL, nullable=True)
    coreOvoIse = db.Column(db.REAL, nullable=True)
    coreOvoOse = db.Column(db.REAL, nullable=True)
    coreDiaIse = db.Column(db.REAL, nullable=True)
    coreDiaOse = db.Column(db.REAL, nullable=True)

class Coating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    common_id = db.Column(db.Integer, nullable=False)
    spoolID = db.Column(db.String(13), unique=True, nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    coat2Dia = db.Column(db.REAL, nullable=True)
    coat2Ovo = db.Column(db.REAL, nullable=True)
    coat2ECC = db.Column(db.REAL, nullable=True)
    coat1Dia = db.Column(db.REAL, nullable=True)
    coat1Ovo = db.Column(db.REAL, nullable=True)

class Chromatic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    common_id = db.Column(db.Integer, nullable=False)
    spoolID = db.Column(db.String(13), unique=True, nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    zwl = db.Column(db.REAL, nullable=True)
    slope = db.Column(db.REAL, nullable=True)
    disp1285 = db.Column(db.REAL, nullable=True)
    disp1290 = db.Column(db.REAL, nullable=True)
    disp1330 = db.Column(db.REAL, nullable=True)
    disp1550 = db.Column(db.REAL, nullable=True)

class PMD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    common_id = db.Column(db.Integer, nullable=False)
    spoolID = db.Column(db.String(13), unique=True, nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    pmd = db.Column(db.REAL, nullable=True)

class MacroBending(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    common_id = db.Column(db.Integer, nullable=False)
    spoolID = db.Column(db.String(13), unique=True, nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    R7_1550 = db.Column(db.REAL, nullable=True)
    R7_1625 = db.Column(db.REAL, nullable=True)
    R10_1550 = db.Column(db.REAL, nullable=True)
    R10_1625 = db.Column(db.REAL, nullable=True)
    R15_1550 = db.Column(db.REAL, nullable=True)
    R15_1625 = db.Column(db.REAL, nullable=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userEmail = db.Column(db.String(30), unique=True, nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)

class Preform(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime(), nullable=False)
    preform = db.Column(db.String(2), unique=True , nullable=False)
    description = db.Column(db.Text(), nullable=False)

class Resin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime(), nullable=False)
    resin = db.Column(db.String(1), unique=True, nullable=False)
    description = db.Column(db.Text(), nullable=False)

class NcrCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime(), nullable=False)
    code = db.Column(db.String(2), unique=True, nullable=False)
    description = db.Column(db.Text(), nullable=False)

class DrawNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime(), nullable=False)
    drawNumber = db.Column(db.String(2), unique=True, nullable=False)