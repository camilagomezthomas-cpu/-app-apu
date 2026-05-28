import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class ApuPresupuestoWidget extends StatefulWidget {
  const ApuPresupuestoWidget({
    super.key,
    this.width,
    this.height,
  });

  final double? width;
  final double? height;

  @override
  State<ApuPresupuestoWidget> createState() => _ApuPresupuestoWidgetState();
}

class _ApuPresupuestoWidgetState extends State<ApuPresupuestoWidget> {
  static const double jornadaHoras = 8.0;
  static const double prestacionesSociales = 1.65;
  static const double herramientaMenorPct = 0.05;

  final _money = NumberFormat.currency(locale: 'es_CO', symbol: r'$ ', decimalDigits: 2);
  final _num = NumberFormat('#,##0.###', 'es_CO');

  String proyecto = 'Proyecto de obra civil';
  String capitulo = 'APU - Presupuesto';
  String actividad = 'Excavación';
  double cantidadObra = 1.0;
  bool calcularGeometria = false;
  bool incluirTransporte = true;

  double baseMenor = 1.80;
  double baseMayor = 2.80;
  double profundidad = 1.50;
  double longitud = 50.0;
  double factorExpansion = 1.25;

  double distanciaBotadero = 15.0;
  double tarifaTransporte = 1500.0;
  double tarifaVertimiento = 80000.0;

  double rendimientoCuadrilla = 20.0;
  double adminPct = 10.0;
  double imprevistosPct = 5.0;
  double utilidadPct = 5.0;

  final Map<String, List<bool>> checklistEstado = {};

  late Map<String, ApuActividad> actividades;

  @override
  void initState() {
    super.initState();
    actividades = _crearActividades();
    for (final key in actividades.keys) {
      checklistEstado[key] = List<bool>.filled(actividades[key]!.checklist.length, false);
    }
  }

  Map<String, ApuActividad> _crearActividades() {
    return {
      'Excavación': ApuActividad(
        unidad: 'm³',
        descripcion: 'Excavación mecánica o manual con cargue, retiro y disposición.',
        checklist: const [
          'Verificar replanteo y niveles antes de iniciar.',
          'Confirmar ancho, profundidad y longitud de excavación según planos.',
          'Revisar estabilidad de taludes o necesidad de entibado.',
          'Verificar uso de EPP y señalización del área.',
          'Controlar cargue, retiro y disposición del material excavado.',
          'Registrar volumen excavado y viajes al botadero.',
          'Validar limpieza final y cotas de fondo.',
        ],
        materiales: const [],
        manoObra: [
          ManoObraItem('Operador retroexcavadora', 1, 127272.73),
          ManoObraItem('Ayudante', 1, 71428.57),
        ],
        equipos: [
          EquipoItem('Retroexcavadora', '75 HP', 1, 90000, 8.30),
          EquipoItem('Volqueta', '6.5 m³', 1, 75000, 6.50),
        ],
      ),
      'Zapata': ApuActividad(
        unidad: 'm³',
        descripcion: 'Construcción de zapata en concreto reforzado.',
        checklist: const [
          'Verificar dimensiones de excavación y cota de desplante.',
          'Confirmar solado, limpieza y nivelación del fondo.',
          'Revisar acero de refuerzo, traslapos y recubrimiento.',
          'Verificar formaleta, alineamiento y estabilidad.',
          'Confirmar resistencia del concreto especificada.',
          'Controlar vibrado, acabado y curado.',
          'Registrar volumen fundido y evidencia fotográfica.',
        ],
        materiales: [
          MaterialItem('Concreto premezclado', 'm³', 1.05, 430000),
          MaterialItem('Acero de refuerzo', 'kg', 95, 6200),
          MaterialItem('Alambre negro', 'kg', 1.2, 6500),
        ],
        manoObra: [
          ManoObraItem('Oficial', 1, 100000),
          ManoObraItem('Ayudante', 2, 71428.57),
        ],
        equipos: [EquipoItem('Vibrador de concreto', 'Eléctrico', 1, 25000, 12.0)],
      ),
      'Vigas': ApuActividad(
        unidad: 'm³',
        descripcion: 'Construcción de vigas en concreto reforzado.',
        checklist: const [
          'Verificar niveles, ejes y dimensiones de viga.',
          'Revisar formaleta, apuntalamiento y desmoldante.',
          'Confirmar acero longitudinal y estribos según plano.',
          'Verificar recubrimientos y separadores.',
          'Controlar vaciado, vibrado y acabado.',
          'Realizar curado y protección del elemento.',
          'Registrar volumen, lote de concreto y observaciones.',
        ],
        materiales: [
          MaterialItem('Concreto premezclado', 'm³', 1.05, 430000),
          MaterialItem('Acero de refuerzo', 'kg', 120, 6200),
          MaterialItem('Formaleta', 'm²', 5.0, 45000),
          MaterialItem('Alambre negro', 'kg', 1.5, 6500),
        ],
        manoObra: [
          ManoObraItem('Oficial', 1, 100000),
          ManoObraItem('Ayudante', 2, 71428.57),
        ],
        equipos: [EquipoItem('Vibrador de concreto', 'Eléctrico', 1, 25000, 10.0)],
      ),
      'Losa aligerada': ApuActividad(
        unidad: 'm²',
        descripcion: 'Construcción de losa aligerada por área de placa.',
        checklist: const [
          'Verificar apuntalamiento, camillas y seguridad inferior.',
          'Confirmar distribución de aligerantes o casetones.',
          'Revisar acero superior, inferior, nervios y refuerzos negativos.',
          'Verificar instalaciones embebidas antes del vaciado.',
          'Controlar espesor de losa, vibrado y acabado.',
          'Garantizar curado y tiempos mínimos de desencofrado.',
          'Registrar área ejecutada y control de calidad.',
        ],
        materiales: [
          MaterialItem('Concreto premezclado', 'm³', 0.12, 430000),
          MaterialItem('Acero de refuerzo', 'kg', 18, 6200),
          MaterialItem('Aligerante', 'und', 1.0, 18000),
          MaterialItem('Formaleta y puntales', 'm²', 1.0, 50000),
        ],
        manoObra: [
          ManoObraItem('Oficial', 1, 100000),
          ManoObraItem('Ayudante', 2, 71428.57),
        ],
        equipos: [EquipoItem('Vibrador de concreto', 'Eléctrico', 1, 25000, 35.0)],
      ),
      'Estructura metálica': ApuActividad(
        unidad: 'kg',
        descripcion: 'Suministro, fabricación, montaje y pintura de estructura metálica.',
        checklist: const [
          'Verificar planos de taller y cantidades de acero.',
          'Revisar certificados del material.',
          'Controlar cortes, perforaciones y soldaduras.',
          'Verificar alineamiento, plomo y nivelación durante montaje.',
          'Revisar torque de pernos y calidad de soldadura.',
          'Aplicar anticorrosivo o pintura especificada.',
          'Registrar kg instalados y liberación de calidad.',
        ],
        materiales: [
          MaterialItem('Acero estructural', 'kg', 1.05, 7200),
          MaterialItem('Soldadura', 'kg', 0.025, 18000),
          MaterialItem('Pintura anticorrosiva', 'kg', 0.015, 22000),
          MaterialItem('Pernos y anclajes', 'kg', 0.03, 15000),
        ],
        manoObra: [
          ManoObraItem('Soldador', 1, 130000),
          ManoObraItem('Ayudante', 1, 71428.57),
          ManoObraItem('Maestro de obra', 0.25, 140000),
        ],
        equipos: [
          EquipoItem('Equipo de soldadura', 'Inversor', 1, 35000, 80.0),
          EquipoItem('Pulidora', 'Industrial', 1, 15000, 120.0),
        ],
      ),
    };
  }

  double get volumenExcavacion {
    if (actividad != 'Excavación') return cantidadObra;
    if (!calcularGeometria) return cantidadObra;
    final areaPerfil = ((baseMenor + baseMayor) / 2) * profundidad;
    return areaPerfil * longitud;
  }

  double get volumenExpansion => volumenExcavacion * factorExpansion;

  double costoEquipoUnitario(EquipoItem e) {
    if (e.rendimientoHora <= 0) return 0;
    return e.cantidad * e.tarifaHora / e.rendimientoHora;
  }

  double costoMaterialUnitario(MaterialItem m) => m.cantidadPorUnidad * m.precioUnitario;

  double costoManoObraUnitario(ManoObraItem m) {
    if (rendimientoCuadrilla <= 0) return 0;
    return m.cantidad * m.jornal * prestacionesSociales / rendimientoCuadrilla;
  }

  List<Map<String, dynamic>> transporteRows() {
    if (actividad != 'Excavación' || !incluirTransporte || volumenExcavacion <= 0) return [];
    final cantidadTransportadaPorM3 = volumenExpansion / volumenExcavacion;
    final m3Km = cantidadTransportadaPorM3 * distanciaBotadero;
    return [
      {
        'item': 'MATERIAL EXCAVADO',
        'distancia': distanciaBotadero,
        'cantidad': cantidadTransportadaPorM3,
        'm3km': m3Km,
        'tarifa': tarifaTransporte,
        'valor': m3Km * tarifaTransporte,
      },
      {
        'item': 'BOTADERO',
        'distancia': null,
        'cantidad': cantidadTransportadaPorM3,
        'm3km': null,
        'tarifa': tarifaVertimiento,
        'valor': cantidadTransportadaPorM3 * tarifaVertimiento,
      },
    ];
  }

  double get subtotalEquipo => actividades[actividad]!.equipos.fold(0, (s, e) => s + costoEquipoUnitario(e));
  double get subtotalMateriales => actividades[actividad]!.materiales.fold(0, (s, m) => s + costoMaterialUnitario(m));
  double get subtotalManoObra => actividades[actividad]!.manoObra.fold(0, (s, m) => s + costoManoObraUnitario(m));
  double get subtotalTransporte => transporteRows().fold(0, (s, r) => s + (r['valor'] as double));
  double get herramientaMenor => subtotalManoObra * herramientaMenorPct;
  double get baseAiu => subtotalEquipo + subtotalMateriales + subtotalTransporte + subtotalManoObra + herramientaMenor;
  double get administracion => baseAiu * adminPct / 100;
  double get imprevistos => baseAiu * imprevistosPct / 100;
  double get utilidad => baseAiu * utilidadPct / 100;
  double get precioUnitario => baseAiu + administracion + imprevistos + utilidad;
  double get valorTotalItem => precioUnitario * cantidadObra;

  @override
  Widget build(BuildContext context) {
    final act = actividades[actividad]!;
    final unidad = act.unidad;
    final checks = checklistEstado[actividad]!;
    final cumplimiento = checks.isEmpty ? 0.0 : checks.where((v) => v).length / checks.length;

    return SizedBox(
      width: widget.width ?? double.infinity,
      height: widget.height,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _titulo(),
            _card('1. Datos generales del proyecto', [
              _textInput('Proyecto', proyecto, (v) => proyecto = v),
              _textInput('Capítulo', capitulo, (v) => capitulo = v),
              _dropdownActividad(),
              _numberInput('Cantidad total de obra ($unidad)', cantidadObra, (v) => cantidadObra = v),
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text('Descripción: ${act.descripcion}\nUnidad de pago del APU: $unidad'),
              ),
            ]),
            if (actividad == 'Excavación') _excavacionCard(),
            _equipoCard(act, unidad),
            _materialesCard(act, unidad),
            _transporteCard(unidad),
            _manoObraCard(act, unidad),
            _resumenCard(unidad),
            _checklistCard(act, checks, cumplimiento),
            _tablaFinal(act, unidad),
          ],
        ),
      ),
    );
  }

  Widget _titulo() => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(color: const Color(0xFF172554), borderRadius: BorderRadius.circular(16)),
        child: const Text('APU - Presupuestos de Obra Civil', style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
      );

  Widget _card(String title, List<Widget> children) => Container(
        width: double.infinity,
        margin: const EdgeInsets.only(top: 16),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), boxShadow: const [BoxShadow(blurRadius: 12, color: Color(0x1A000000))]),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Wrap(spacing: 12, runSpacing: 12, children: children),
        ]),
      );

  Widget _textInput(String label, String value, Function(String) onChanged) => SizedBox(
        width: 320,
        child: TextFormField(
          initialValue: value,
          decoration: InputDecoration(labelText: label, border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
          onChanged: (v) => setState(() => onChanged(v)),
        ),
      );

  Widget _numberInput(String label, double value, Function(double) onChanged) => SizedBox(
        width: 250,
        child: TextFormField(
          initialValue: value.toStringAsFixed(value % 1 == 0 ? 0 : 2),
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          decoration: InputDecoration(labelText: label, border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
          onChanged: (v) => setState(() => onChanged(double.tryParse(v.replaceAll(',', '.')) ?? 0)),
        ),
      );

  Widget _dropdownActividad() => SizedBox(
        width: 280,
        child: DropdownButtonFormField<String>(
          value: actividad,
          decoration: InputDecoration(labelText: 'Actividad APU', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
          items: actividades.keys.map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
          onChanged: (v) => setState(() {
            actividad = v ?? actividad;
            rendimientoCuadrilla = actividad == 'Estructura metálica' ? 350 : 20;
          }),
        ),
      );

  Widget _excavacionCard() => _card('2. Cálculo de cantidad de excavación', [
        SizedBox(
          width: 320,
          child: SwitchListTile(
            title: const Text('Calcular por geometría'),
            value: calcularGeometria,
            onChanged: (v) => setState(() => calcularGeometria = v),
          ),
        ),
        if (calcularGeometria) ...[
          _numberInput('Base menor B1 (m)', baseMenor, (v) => baseMenor = v),
          _numberInput('Base mayor B2 (m)', baseMayor, (v) => baseMayor = v),
          _numberInput('Profundidad H (m)', profundidad, (v) => profundidad = v),
          _numberInput('Longitud L (m)', longitud, (v) => longitud = v),
        ],
        _numberInput('Factor de expansión', factorExpansion, (v) => factorExpansion = v),
        SizedBox(
          width: 320,
          child: SwitchListTile(
            title: const Text('Incluir transporte y botadero'),
            value: incluirTransporte,
            onChanged: (v) => setState(() => incluirTransporte = v),
          ),
        ),
        _infoBox('Volumen excavación: ${_num.format(volumenExcavacion)} m³\nCantidad transportada automática: ${_num.format(volumenExpansion)} m³'),
      ]);

  Widget _equipoCard(ApuActividad act, String unidad) => _card('3. Equipo - rendimiento real por hora', [
        _infoBox('Fórmula: costo equipo por $unidad = cantidad × tarifa hora / rendimiento ($unidad/h).'),
        _table(
          columns: const ['Equipo', 'Tipo', 'Cant.', 'Tarifa/h', 'Rend.', 'V. unitario'],
          rows: act.equipos.map((e) => [
            e.nombre,
            e.tipo,
            _num.format(e.cantidad),
            _money.format(e.tarifaHora),
            '${_num.format(e.rendimientoHora)} $unidad/h',
            _money.format(costoEquipoUnitario(e)),
          ]).toList(),
        ),
        Text('Sub-total Equipo / $unidad: ${_money.format(subtotalEquipo)}', style: const TextStyle(fontWeight: FontWeight.bold)),
      ]);

  Widget _materialesCard(ApuActividad act, String unidad) => _card('4. Materiales', [
        if (act.materiales.isEmpty) const Text('Esta actividad no tiene materiales directos registrados.'),
        if (act.materiales.isNotEmpty)
          _table(
            columns: const ['Material', 'Und', 'Cant/und obra', 'Precio', 'V. unitario'],
            rows: act.materiales.map((m) => [m.nombre, m.unidad, _num.format(m.cantidadPorUnidad), _money.format(m.precioUnitario), _money.format(costoMaterialUnitario(m))]).toList(),
          ),
        Text('Sub-total Materiales / $unidad: ${_money.format(subtotalMateriales)}', style: const TextStyle(fontWeight: FontWeight.bold)),
      ]);

  Widget _transporteCard(String unidad) => _card('5. Transporte y disposición', [
        if (actividad == 'Excavación' && incluirTransporte) ...[
          _numberInput('Distancia al botadero (km)', distanciaBotadero, (v) => distanciaBotadero = v),
          _numberInput(r'Tarifa transporte ($/m³-km)', tarifaTransporte, (v) => tarifaTransporte = v),
          _numberInput(r'Tarifa botadero ($/m³)', tarifaVertimiento, (v) => tarifaVertimiento = v),
          _infoBox('No se digita manualmente la cantidad transportada. Sale del volumen de expansión: ${_num.format(volumenExpansion)} m³.'),
          _table(
            columns: const ['Ítem', 'Distancia', 'Cantidad', 'm³-km', 'Tarifa', 'V. unitario'],
            rows: transporteRows().map((r) => [
              r['item'].toString(),
              r['distancia'] == null ? '-' : _num.format(r['distancia']),
              _num.format(r['cantidad']),
              r['m3km'] == null ? '-' : _num.format(r['m3km']),
              _money.format(r['tarifa']),
              _money.format(r['valor']),
            ]).toList(),
          ),
        ] else
          const Text('Esta actividad no requiere transporte de material excavado.'),
        Text('Sub-total Transporte / $unidad: ${_money.format(subtotalTransporte)}', style: const TextStyle(fontWeight: FontWeight.bold)),
      ]);

  Widget _manoObraCard(ApuActividad act, String unidad) => _card('6. Mano de obra', [
        _numberInput('Rendimiento de cuadrilla ($unidad/día)', rendimientoCuadrilla, (v) => rendimientoCuadrilla = v),
        _table(
          columns: const ['Trabajador', 'Cant.', 'Jornal', 'Prest.', 'Jornal total', 'Rend/día', 'V. unitario'],
          rows: act.manoObra.map((m) => [
            m.nombre,
            _num.format(m.cantidad),
            _money.format(m.jornal),
            _num.format(prestacionesSociales),
            _money.format(m.jornal * prestacionesSociales),
            _num.format(rendimientoCuadrilla),
            _money.format(costoManoObraUnitario(m)),
          ]).toList(),
        ),
        Text('Sub-total Mano de Obra / $unidad: ${_money.format(subtotalManoObra)}', style: const TextStyle(fontWeight: FontWeight.bold)),
      ]);

  Widget _resumenCard(String unidad) => _card('7. Resumen del APU', [
        _numberInput('Administración (%)', adminPct, (v) => adminPct = v),
        _numberInput('Imprevistos (%)', imprevistosPct, (v) => imprevistosPct = v),
        _numberInput('Utilidad (%)', utilidadPct, (v) => utilidadPct = v),
        _table(columns: const ['Concepto', 'Valor'], rows: [
          ['Sub-total Equipo / $unidad', _money.format(subtotalEquipo)],
          ['Sub-total Materiales / $unidad', _money.format(subtotalMateriales)],
          ['Sub-total Transporte / $unidad', _money.format(subtotalTransporte)],
          ['Sub-total Mano de Obra / $unidad', _money.format(subtotalManoObra)],
          ['Herramienta menor 5% M.O.', _money.format(herramientaMenor)],
          ['Administración', _money.format(administracion)],
          ['Imprevistos', _money.format(imprevistos)],
          ['Utilidad', _money.format(utilidad)],
          ['PRECIO UNITARIO APU / $unidad', _money.format(precioUnitario)],
          ['VALOR TOTAL DEL ÍTEM', _money.format(valorTotalItem)],
        ]),
      ]);

  Widget _checklistCard(ApuActividad act, List<bool> checks, double cumplimiento) => _card('8. Lista de chequeo en campo', [
        SizedBox(width: 600, child: LinearProgressIndicator(value: cumplimiento, minHeight: 10)),
        Text('Cumplimiento: ${(cumplimiento * 100).toStringAsFixed(1)}%'),
        ...List.generate(act.checklist.length, (i) => SizedBox(
              width: 700,
              child: CheckboxListTile(
                value: checks[i],
                title: Text(act.checklist[i]),
                onChanged: (v) => setState(() => checks[i] = v ?? false),
              ),
            )),
      ]);

  Widget _tablaFinal(ApuActividad act, String unidad) => _card('9. Tabla final del APU', [
        _infoBox('APU: $actividad | Unidad: $unidad | Proyecto: $proyecto | Capítulo: $capitulo'),
        _table(columns: const ['Concepto', 'Valor'], rows: [
          ['Costo directo + herramienta menor', _money.format(baseAiu)],
          ['AIU total', _money.format(administracion + imprevistos + utilidad)],
          ['Precio unitario', _money.format(precioUnitario)],
          ['Cantidad de obra', '${_num.format(cantidadObra)} $unidad'],
          ['Valor total', _money.format(valorTotalItem)],
        ]),
      ]);

  Widget _infoBox(String text) => Container(
        width: 420,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFFBFDBFE))),
        child: Text(text),
      );

  Widget _table({required List<String> columns, required List<List<String>> rows}) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        headingRowColor: WidgetStateProperty.all(const Color(0xFFE5E7EB)),
        columns: columns.map((c) => DataColumn(label: Text(c, style: const TextStyle(fontWeight: FontWeight.bold)))).toList(),
        rows: rows.map((r) => DataRow(cells: r.map((v) => DataCell(Text(v))).toList())).toList(),
      ),
    );
  }
}

class ApuActividad {
  ApuActividad({
    required this.unidad,
    required this.descripcion,
    required this.checklist,
    required this.materiales,
    required this.manoObra,
    required this.equipos,
  });

  final String unidad;
  final String descripcion;
  final List<String> checklist;
  final List<MaterialItem> materiales;
  final List<ManoObraItem> manoObra;
  final List<EquipoItem> equipos;
}

class EquipoItem {
  EquipoItem(this.nombre, this.tipo, this.cantidad, this.tarifaHora, this.rendimientoHora);
  final String nombre;
  final String tipo;
  double cantidad;
  double tarifaHora;
  double rendimientoHora;
}

class MaterialItem {
  MaterialItem(this.nombre, this.unidad, this.cantidadPorUnidad, this.precioUnitario);
  final String nombre;
  final String unidad;
  double cantidadPorUnidad;
  double precioUnitario;
}

class ManoObraItem {
  ManoObraItem(this.nombre, this.cantidad, this.jornal);
  final String nombre;
  double cantidad;
  double jornal;
}
