# Prompt de mejoras — AnnyPos

_Generado el 24 de septiembre de 2026 a partir del analisis del documento "AnnyPos - Contenido del sistema de ventas" (8 areas, 43 pantallas y secciones, 628 funciones documentadas). 37 hallazgos, verificados y auditados uno por uno contra ese documento._

## Como usar este documento

Este documento es un prompt de implementación armado a partir de un análisis del contenido documentado del sistema AnnyPos (sistema de ventas para joyerías, Bolivia): una revisión módulo por módulo —Ventas y caja, Joyas e inventario, Clientes y portal de clientas, Reparaciones (taller), Resumen/ganancia y gastos, Tienda en línea (WooCommerce), Administración y ajustes, y detalles menores de plantilla— que describe comportamientos observados, pantallas o funciones faltantes, permisos huérfanos y validaciones ausentes, junto con una propuesta concreta de qué construir o corregir en cada caso y cómo comprobar que quedó bien. Se redactó revisando la documentación funcional y de contenido del sistema, no el código fuente en sí, por lo que se espera que un ingeniero o agente de código tome cada hallazgo, lo revise primero contra el código real para confirmar si el comportamiento descrito sigue vigente tal cual (puede que ya se haya corregido, que exista lógica de backend sin conectar a ninguna pantalla, o que el hallazgo esté desactualizado), y recién entonces implemente la corrección propuesta, ajustándola si lo que encuentra en el código difiere de lo documentado.

Este archivo esta pensado para pegarse, completo o por seccion, como instruccion a un ingeniero o a un agente de codigo que trabaje sobre el repositorio real de AnnyPos (ese codigo no vive en este repositorio). El repositorio `bronstor/bronstor` solo guarda este documento como referencia/backlog.

## Orden de prioridad sugerido

1. Pedido "Entregado" se marca como pagado sin confirmar el cobro
2. Precio mínimo (tope de descuento) sin ninguna validación
3. Falta pantalla para registrar el pago de un saldo pendiente
4. Falta "Olvidé mi contraseña" y las políticas de contraseña son inconsistentes e inseguras
5. Stock se descuenta con pedidos web sin pagar y permite negativos
6. Multi-almacén roto en Nuevo ajuste y Stock inicial
7. No existe pantalla para registrar devoluciones
8. Tarjetas "Total comprado" y "Por cobrar" solo cuentan la página visible
9. Botones Editar/Eliminar visibles sin permiso en Lista de ventas
10. Compras a proveedores sin módulo que las respalde

## Hallazgos por area

## 1. Ventas y caja

### Falta pantalla para registrar el pago de un saldo pendiente

**Que pasa hoy:** El sistema permite dejar ventas a cuenta (saldo pendiente) y existe el permiso "Cobrar saldos pendientes" dentro del módulo Pagos, pero no hay ninguna pantalla ni botón donde el personal de la joyería pueda registrar que esa deuda ya fue pagada. La pestaña "Pagos" del Detalle de cliente solo muestra el historial (Fecha, Recibo, Nota, Método, Monto); no tiene ningún botón de acción, y el Portal de clientas ("Mis pagos") es de solo consulta y le indica a la clienta que puede "cancelarlo en la joyería", es decir, el pago se recibe en persona pero el sistema no ofrece dónde anotarlo.

**Por que importa:** La joyería no tiene forma de cerrar el ciclo de una venta a crédito: el saldo queda pendiente para siempre en el sistema aunque la clienta ya haya pagado en efectivo o por otro medio, lo que genera descuadres de caja (el efectivo recibido no queda registrado) y deja las tarjetas y reportes de "Por cobrar" (Lista de clientes, Resumen) mostrando montos que en realidad ya se cobraron.

**Que hacer:**
- Buscar en el código dónde se usa o valida el permiso "Cobrar saldos pendientes" (backend y frontend) para confirmar si ya existe lógica de negocio sin interfaz, o si el permiso está huérfano.
- Diseñar y construir un flujo "Registrar pago de saldo" con los mismos campos que "Registrar pago" de trabajos de taller: Monto (Bs) prellenado con el saldo pendiente, Fecha (por defecto hoy), Método de pago (lista) y Nota opcional; reutilizar validaciones equivalentes a las del taller (no permitir monto cero ni cobrar de más).
- Exponer el botón/acceso desde Lista de ventas (en cada venta con saldo pendiente, junto a la columna "Debe") y desde Detalle de cliente (en la pestaña Pagos o junto a la tarjeta/monto "Por cobrar").
- Actualizar tras el pago: el saldo pendiente de la venta, el estado de pago (Pendiente/Parcial/Pagado), el monto "Debe" del cliente y el historial de pagos del cliente (agregando la nueva fila con su recibo, fecha, método y monto en la pestaña Pagos).

**Como comprobar que quedo bien:**
- Desde una venta con saldo pendiente en Lista de ventas y desde el Detalle de cliente se puede abrir "Registrar pago de saldo", cobrar un monto y ver que el saldo pendiente se reduce o llega a cero en ambas pantallas, y que aparece la fila nueva en la pestaña Pagos del cliente.
- El permiso "Cobrar saldos pendientes" efectivamente restringe el acceso a ese flujo (un usuario sin el permiso no puede abrir ni confirmar el registro del pago).

### No existe pantalla para registrar devoluciones

**Que pasa hoy:** El sistema menciona devoluciones en varios puntos (bloquean Editar/Eliminar venta cuando "Tiene una devolución registrada", pestaña "Devoluciones" en el Detalle de cliente con columnas Nota/Fecha/Estado/Total/Pagado/Debe, tarjeta "A favor del cliente" para devoluciones sin reembolsar, columna "Devoluciones" en la tabla de Proveedores) pero no hay ninguna pantalla donde se pueda registrar una devolución nueva.

**Por que importa:** Sin un flujo real de registro, esas pestañas y tarjetas de devoluciones quedan siempre vacías o desactualizadas, y la joyería no tiene forma de documentar una pieza devuelta, reflejar el "a favor del cliente" ni descontar/reingresar stock correctamente.

**Que hacer:**
- Revisar el modelo de datos actual (tablas/entidades de ventas, clientes y proveedores) para confirmar si ya existe una entidad "Devolución" sin UI, o si hay que crearla desde cero.
- Construir la pantalla de registro de devolución accesible desde el Detalle de venta (o desde la pestaña "Devoluciones" del cliente): seleccionar la nota de venta, las joyas y cantidades a devolver, motivo, y si se reembolsa en efectivo o queda "a favor del cliente"; al guardar, generar el código de devolución que se muestra como "Nota" en la pestaña Devoluciones del cliente.
- Conectar el registro con: reingreso de stock, actualización de la tarjeta "A favor del cliente" y de la pestaña "Devoluciones" en Detalle de cliente, y con el flujo equivalente de devoluciones a proveedores si aplica al mismo módulo.
- Revisar y, si falta, implementar la regla que bloquea Editar/Eliminar de una venta que ya tiene devolución asociada.

**Como comprobar que quedo bien:**
- Se puede crear una devolución desde una venta existente, y esa devolución aparece en la pestaña "Devoluciones" del Detalle de cliente con su Nota, Fecha, Estado, Total, Pagado y Debe.
- Tras registrar la devolución, el stock de la joya devuelta se actualiza y (si corresponde) la tarjeta "A favor del cliente" refleja el monto pendiente de reembolso.
- Intentar Editar o Eliminar la venta original muestra el aviso "Tiene una devolución registrada" y bloquea la acción.

### El boton "Vaciar" de Venta actual borra la venta sin confirmar

**Que pasa hoy:** En el panel "Venta actual" de la pantalla Vender, el botón "Vaciar" borra toda la venta en curso sin pedir confirmación, a diferencia de otras acciones destructivas del sistema (por ejemplo, "Eliminar cliente" o el botón "Vaciar" del registro de sincronización en Tienda en línea, que sí muestran un diálogo de confirmación).

**Por que importa:** Un toque accidental en "Vaciar" hace perder de golpe todas las joyas ya agregadas a la venta, obligando a repetir el escaneo/selección completo, lo cual es especialmente costoso en ventas con muchas piezas o en el flujo de celular.

**Que hacer:**
- Localizar el manejador del botón "Vaciar" en el panel "Venta actual" (pantalla Vender) en el código frontend.
- Agregar un diálogo de confirmación antes de ejecutar el vaciado, siguiendo el mismo componente/patrón usado en otras confirmaciones del sistema (por ejemplo, la de "Eliminar cliente" o la de "Vaciar" el registro de sincronización).
- Redactar el texto de confirmación en el mismo tono que el resto del sistema (pregunta clara + explicación de la consecuencia, p.ej. "¿Vaciar la venta actual? Se perderán todas las joyas agregadas.").
- Verificar que la confirmación aplique tanto en la vista de escritorio como en la vista de celular (barra flotante "Venta nueva · Ver venta" y la venta a pantalla completa).

**Como comprobar que quedo bien:**
- Al tocar "Vaciar" con productos en la venta actual aparece un diálogo de confirmación y la venta solo se borra si se confirma; al cancelar, la venta actual queda intacta.
- El comportamiento es consistente en escritorio y en celular (incluyendo la venta abierta a pantalla completa desde la barra flotante).

## 2. Joyas e inventario

### Compras a proveedores sin módulo que las respalde

**Que pasa hoy:** La pantalla Proveedores muestra las cifras "Comprado" y "Por pagar" por proveedor, pero en el sistema no existe ningún módulo de compras (registrar qué se le compró) ni de pagos a proveedores que alimente esos números.

**Por que importa:** Son cifras que la dueña de la joyería usa para saber cuánto le debe a cada proveedor; sin un módulo real que las alimente, esos totales no tienen ningún proceso que los mantenga actualizados, por lo que no reflejan lo que realmente se compró ni se pagó, y la dueña no puede confiar en ellos para decidir cuánto y a quién pagar.

**Que hacer:**
- Ubicar en el código de dónde salen hoy los valores "Comprado" y "Por pagar" en la ficha/tabla de Proveedores (columna calculada, campo fijo, u otra fuente).
- Diseñar y construir el módulo de Compras: registrar una compra a un proveedor con sus joyas, cantidades, costo y el almacén al que ingresa la mercadería, y que además incremente el stock de ese almacén.
- Construir el registro de Pagos a proveedores (abonos y saldo), de forma que "Por pagar" sea Comprado menos Pagado.
- Conectar ambos módulos a las tarjetas y la tabla que ya existen en Proveedores para que dejen de mostrar datos huérfanos.

**Como comprobar que quedo bien:**
- Registrar una compra a un proveedor y verificar que "Comprado" sube en su fila/ficha.
- Registrar un pago parcial de esa compra y verificar que "Por pagar" baja en la cifra correspondiente.

### Multi-almacén roto en Nuevo ajuste y Stock inicial

**Que pasa hoy:** En "Nuevo ajuste" no se puede elegir el almacén: el ajuste siempre se aplica en el primer almacén registrado. Lo mismo ocurre con el "Stock inicial" al crear una joya: las piezas siempre quedan en el primer almacén.

**Por que importa:** En una joyería con más de un local o depósito, el inventario queda mal repartido: el stock se carga o ajusta en el almacén equivocado, generando descuadres que confunden a la vendedora en el punto de venta y distorsionan el "Stock por almacén" y los reportes.

**Que hacer:**
- Ubicar en el backend/frontend de "Nuevo ajuste" dónde se fija el almacén (probablemente un valor por defecto tipo "primer almacén" sin exponer selector).
- Agregar al formulario de Nuevo ajuste el mismo selector de almacén que ya existe en Vender y Añadir venta, y usar ese valor al guardar el ajuste.
- Hacer el mismo cambio en el formulario de Añadir producto para el campo "Stock inicial": permitir elegir en qué almacén entra ese stock cuando hay más de uno.
- Revisar el servicio/lógica de guardado de inventario para que reciba y respete el almacén elegido en vez de tomar uno fijo.

**Como comprobar que quedo bien:**
- Con 2 o más almacenes creados, hacer un "Nuevo ajuste" eligiendo un almacén distinto al primero y confirmar que el stock cambia en ese almacén y no en otro.
- Crear una joya con "Stock inicial" eligiendo un almacén distinto al primero y confirmar en el "Stock por almacén" del detalle de la joya que la cantidad quedó en el almacén elegido.

### No existen transferencias de stock entre almacenes

**Que pasa hoy:** Cada almacén lleva su propio inventario, pero no hay ninguna pantalla ni función para transferir piezas de un almacén a otro.

**Por que importa:** Sin transferencias, la única forma de mover mercadería entre local y depósito (o entre sucursales) es "quitar" stock en un almacén y "agregar" en otro por separado con Ajustar stock, lo cual es propenso a errores, no deja registro de que fue una transferencia y complica el control real del inventario.

**Que hacer:**
- Revisar el modelo de datos de almacenes y de los ajustes de stock existentes para ver si se puede reutilizar esa misma estructura de movimientos para modelar una transferencia como un par de movimientos vinculados (salida en origen, entrada en destino).
- Construir una pantalla "Nueva transferencia": elegir almacén origen, almacén destino, joyas y cantidades, validando que no se transfiera más de lo disponible en el origen.
- Registrar la transferencia en un historial (similar a Ajustes de stock) que muestre origen, destino, fecha y usuario.
- Definir si necesita un permiso propio en Roles y permisos, ya que hoy no hay ninguno para esta función.

**Como comprobar que quedo bien:**
- Transferir piezas del almacén A al almacén B y confirmar que el stock baja en A y sube en B en la misma cantidad.
- Confirmar que la transferencia queda visible en un historial trazable (fecha, almacenes, usuario).

### Precio mayorista guardado pero nunca usado en ventas

**Que pasa hoy:** El campo "Precio mayorista (Bs)" se guarda en la ficha de la joya (Añadir/Editar producto), pero ni en Vender ni en Añadir venta se usa ese precio al armar la venta: siempre se cobra el precio de venta normal.

**Por que importa:** La joyería no puede ofrecer precio de mayorista a clientas que compran por volumen; sin esa opción en el flujo de venta, la única forma de aproximarlo hoy es con el descuento general de la venta, sin control automático ni trazabilidad de cuándo se vendió al por mayor.

**Que hacer:**
- Confirmar en el modelo/servicio de la joya que el "precio mayorista" ya se persiste correctamente y está disponible para el flujo de venta.
- Definir la regla de negocio (cantidad mínima, tipo de cliente, o selección manual del vendedor) si no está ya especificada en otro lugar del sistema.
- Implementar en Vender y en Añadir venta la opción de aplicar el precio mayorista al agregar o editar la línea de una joya en la venta.
- Reflejar el precio realmente cobrado (normal o mayorista) en el resumen de la venta, la nota de venta y el ticket.

**Como comprobar que quedo bien:**
- Vender una joya que tiene precio mayorista cargado, aplicar ese precio en la venta y confirmar que la nota de venta y el ticket lo reflejan.
- Vender una joya sin precio mayorista definido y confirmar que el flujo normal no se rompe.

### Precio mínimo (tope de descuento) sin ninguna validación

**Que pasa hoy:** "Precio mínimo (Bs)" se describe como "tope de descuento" en la ficha de la joya, pero no se usa en ninguna validación de venta: en Vender, la ventana "Cobrar venta" solo bloquea el descuento cuando supera el subtotal; en Añadir venta y Editar venta existe el mismo tipo de campo de descuento, sin que se documente que se compare contra el precio mínimo de cada joya. En ningún caso el sistema valida el descuento contra el "Precio mínimo" definido en la ficha de la joya.

**Por que importa:** Una vendedora puede aplicar un descuento que deje el precio efectivo de una joya por debajo de su costo o del piso que definió la dueña, sin ningún aviso ni bloqueo, generando pérdidas silenciosas venta tras venta.

**Que hacer:**
- Ubicar la validación actual del descuento (la regla "no puede pasar del subtotal", documentada en Vender/Cobrar venta) en el backend/frontend de Vender, Añadir venta y Editar venta, y confirmar si Añadir venta y Editar venta aplican esa misma regla o ninguna.
- Definir cómo debe aplicar el tope cuando hay varias joyas en una misma venta (por línea individual o por precio efectivo del total) si esto no está ya resuelto en otra parte del sistema.
- Agregar la validación para que el descuento no deje el precio efectivo de una joya por debajo de su "Precio mínimo", cuando ese campo esté definido en su ficha.
- Mostrar un aviso claro al vendedor cuando el descuento ingresado exceda el tope permitido por el precio mínimo.

**Como comprobar que quedo bien:**
- Con una joya que tenga "Precio mínimo" definido, intentar un descuento que baje el precio por debajo de ese mínimo y confirmar que el sistema lo bloquea o avisa.
- Confirmar que joyas sin "Precio mínimo" definido siguen comportándose igual que hoy (solo tope por subtotal).

### Permiso "Imprimir etiquetas" sin ninguna función asociada

**Que pasa hoy:** En Roles y permisos existe el permiso "Imprimir etiquetas" (dentro del módulo Joyas), pero no hay ninguna pantalla ni botón en el sistema para imprimir etiquetas de código de barras de las joyas.

**Por que importa:** La joyería no puede generar etiquetas físicas con código de barras para pegar en cada pieza, lo que dificulta usar el lector de código de barras en Vender o Nuevo ajuste con joyas nuevas (obliga a escribir el código a mano); además, el permiso existe pero no protege ninguna función real, lo que confunde al configurar roles.

**Que hacer:**
- Revisar el código de barras que ya se genera y muestra por joya (visible hoy en "Detalle de joya", tarjeta "Código de barras", tipo CODE128) para reutilizarlo como fuente de la etiqueta.
- Construir la función "Imprimir etiquetas": individual desde el Detalle de joya y en lote desde Lista de productos, generando una hoja/PDF imprimible con código de barras, nombre y precio de cada joya.
- Conectar esa función al permiso "Imprimir etiquetas" ya existente en Roles y permisos para que efectivamente controle quién la ve.
- Definir un tamaño de etiqueta pequeño tipo joyero (distinto de la hoja A4 que ya usa el botón "Imprimir" de Detalle de joya) en el diseño de impresión.

**Como comprobar que quedo bien:**
- Con el permiso "Imprimir etiquetas" activo, generar la impresión de una o varias joyas y confirmar que el PDF/hoja trae el código de barras real de cada una.
- Quitar el permiso a un rol y confirmar que la opción deja de estar disponible para ese rol.

### Permiso "Cambiar el precio al vender" sin ninguna función asociada

**Que pasa hoy:** El permiso "Cambiar el precio al vender" existe en Roles y permisos (dentro del módulo Joyas), pero en la pantalla Vender no aparece ninguna forma de editar el precio de una joya al agregarla a la venta.

**Por que importa:** En una joyería suele hacer falta ajustar el precio en el momento (negociación, pieza con algún detalle, promoción puntual); hoy solo se puede simular con el descuento general de la venta, que no queda registrado como un cambio de precio por pieza y no respeta el control de permisos pensado específicamente para esto.

**Que hacer:**
- Revisar el panel "Venta actual" en Vender (donde ya se muestra cantidad, precio c/u y total por línea) y agregar la posibilidad de editar el precio c/u de una línea al agregarla o mientras está en la venta.
- Condicionar esa edición a que el usuario tenga el permiso "Cambiar el precio al vender", ocultando o bloqueando el control si no lo tiene.
- Reflejar el precio editado en el subtotal de la venta, la nota de venta y el ticket, de forma que quede claro que difiere del precio de catálogo.
- Evaluar si Añadir venta necesita el mismo control, ya que tampoco lo tiene hoy.

**Como comprobar que quedo bien:**
- Con el permiso activo, cambiar el precio de una joya al agregarla en Vender y confirmar que el total de la venta y la nota reflejan el precio editado.
- Sin el permiso, confirmar que no aparece ninguna opción para editar el precio de la línea.
</markdown>

## 3. Clientes y portal de clientas

### Tarjetas "Total comprado" y "Por cobrar" solo cuentan la página visible

**Que pasa hoy:** En la Lista de clientes, las tarjetas "Total comprado" y "Por cobrar" se calculan únicamente con las clientas que se muestran en la página actual (30 por página), no con el total de todas las clientas registradas.

**Por que importa:** El dueño de la joyería puede tomar decisiones de cobranza o flujo de caja creyendo que esas cifras son el total real del negocio, cuando en realidad cambian según la página en la que esté parado y solo reflejan una fracción de las clientas (por ejemplo, con 90 clientas en 3 páginas, "Por cobrar" en la página 1 no incluye lo que deben las clientas de las páginas 2 y 3).

**Que hacer:**
- Ubicar en el código dónde se calculan esas dos tarjetas de la Lista de clientes y confirmar si usan el arreglo ya paginado (30 registros) en vez de una consulta agregada sobre toda la tabla de clientes.
- Reemplazar el cálculo por una consulta (o endpoint) que sume "Comprado" y "Debe" sobre el total de clientas, respetando los filtros de búsqueda activos si los hay, independiente de la paginación.
- Si el agregado sobre toda la tabla resulta costoso, calcularlo con una suma en el backend (SQL), no iterando registros en el frontend.
- Tomar como referencia que en Lista de ventas las tarjetas "Total", "Pagado" y "Por cobrar" sí se calculan sobre el total de resultados filtrados y no solo sobre la página visible (30 ventas por página); replicar ese mismo enfoque en Lista de clientes, y de paso revisar si alguna otra pantalla paginada con tarjetas de totales tiene el mismo problema que Clientes.

**Como comprobar que quedo bien:**
- Con más de 30 clientas registradas, "Total comprado" y "Por cobrar" muestran el mismo valor sin importar en qué página esté el usuario, y coinciden con la suma real de todas las clientas.
- Al aplicar una búsqueda/filtro, las tarjetas reflejan la suma de todos los resultados filtrados, no solo de la página visible de esos resultados.

### "Saldo inicial" de la clienta no tiene formulario para cargarlo

**Que pasa hoy:** El Portal de clientas muestra un "Saldo inicial" en Inicio (Resumen de tu cuenta) y en Estado de cuenta, pero en ninguna pantalla del sistema —ni el formulario de Nuevo/Editar cliente, ni la ficha Detalle de cliente, ni el registro manual de pagos ("Registrar pago", que además está atado a una nota de venta específica y no a un saldo inicial)— existe un campo o control para que la joyería cargue o edite ese saldo inicial.

**Por que importa:** Sin una forma de ingresarlo desde la interfaz, el saldo inicial que ve la clienta depende de que alguien lo inserte manualmente en la base de datos o simplemente queda en cero; esto produce un estado de cuenta incorrecto para clientas que ya tenían saldo a favor o en contra antes de empezar a usar AnnyPos, y le resta confianza a la clienta en las cifras del Portal.

**Que hacer:**
- Confirmar en el modelo de datos si ya existe un campo de saldo inicial por clienta; si existe pero no se puede cargar desde ninguna pantalla, identificar de dónde lo están leyendo hoy Portal – Inicio y Portal – Estado de cuenta (carga manual en base de datos, importación inicial, o si simplemente siempre vale cero).
- Agregar un campo "Saldo inicial" al formulario de "Nuevo cliente" / "Editar cliente" (o a la ficha Detalle de cliente), con validación numérica y soporte para valores a favor o en contra.
- Asegurar que ese saldo inicial se incluya correctamente en "Por cobrar", "Saldo actual" y en Estado de cuenta como primer movimiento, antes de compras y pagos.
- Definir qué permiso controla la edición del saldo inicial, ya que afecta directamente el estado de cuenta de la clienta.

**Como comprobar que quedo bien:**
- Se puede crear o editar una clienta, ingresar un "Saldo inicial" distinto de cero, y ese valor aparece correctamente en Portal – Inicio y Portal – Estado de cuenta.
- El "Saldo actual" y las tarjetas "Por cobrar" (sistema y Portal) incluyen ese saldo inicial en sus cálculos.
- El campo "Saldo inicial" solo aparece editable para quien tiene el permiso definido para ello; un rol sin ese permiso no puede modificarlo.

### Falta "Olvidé mi contraseña" y las políticas de contraseña son inconsistentes e inseguras

**Que pasa hoy:** Ni el inicio de sesión del personal ni la entrada del Portal de clientas ofrecen "Olvidé mi contraseña". Además, la política mínima difiere entre ambos (6 caracteres para usuarios del sistema, 8 para el portal), y en los formularios donde se crea o asigna la contraseña (Usuarios y Acceso al portal) esta se escribe a la vista en texto plano, sin opción de ocultarla (el campo de contraseña para iniciar sesión sí se oculta con puntitos; el problema es solo al crear o asignar la contraseña).

**Por que importa:** Sin recuperación de contraseña, cualquier usuaria del personal o clienta que la olvide queda bloqueada y depende de que un administrador se la resetee manualmente. La diferencia entre 6 y 8 caracteres muestra que no hay una política de seguridad centralizada, y mostrar la contraseña en texto plano en pantalla expone credenciales de acceso al sistema de ventas y al Portal frente a cualquiera que esté cerca de la pantalla o vea una captura.

**Que hacer:**
- Implementar un flujo de "Olvidé mi contraseña" por correo (el dato con el que se entra) tanto en Iniciar sesión (personal) como en la entrada del Portal de clientas.
- Unificar el mínimo de caracteres entre usuarios del sistema y clientas del portal (por ejemplo, adoptar los 8 caracteres que ya exige hoy el portal en lugar de los 6 actuales de Usuarios) y centralizar esa validación en un solo lugar del código en vez de duplicarla en cada formulario.
- Cambiar los campos de contraseña en Usuarios y en Acceso al portal para que se oculten por defecto (tipo password, con puntitos), con un botón opcional de mostrar/ocultar en vez de texto plano permanente.
- Aprovechar el cambio para confirmar que las contraseñas se guardan con hash seguro en el backend, independientemente de cómo se muestren en pantalla.

**Como comprobar que quedo bien:**
- Desde Iniciar sesión y desde la entrada del Portal de clientas hay un enlace "Olvidé mi contraseña" que permite recuperar el acceso sin depender de un administrador.
- Al crear o editar una contraseña (usuario del sistema o acceso al portal), el campo se ve oculto por defecto y el mínimo de caracteres exigido es el mismo y está documentado en ambos flujos.
- En la base de datos, la contraseña guardada no corresponde al texto ingresado sino a un hash: no se puede leer en claro ni en la tabla de usuarios del sistema ni en la de acceso al portal.

## 4. Reparaciones (taller)

### Materiales y mano de obra sin lugar donde cargarlos
**Que pasa hoy:** En la Ficha de reparación, la sección "Diagnóstico y presupuesto" muestra la lista de materiales y mano de obra (cantidad × precio y total), pero el propio texto aclara que "solo se ven, no se cargan desde aquí"; en ningún otro punto del documento aparece una pantalla o formulario donde esos ítems se registren.
**Por que importa:** Sin un lugar para cargar materiales y mano de obra, el presupuesto y el desglose de "Cobro" no tienen cómo llenarse con datos reales, lo que traba la cotización y el cobro de cada reparación.
**Que hacer:**
- Revisar el código de la Ficha de reparación (sección Diagnóstico y presupuesto) y confirmar si existe algún endpoint o formulario ya construido pero no enlazado desde la UI.
- Si no existe, construir el formulario para agregar, editar y eliminar líneas de materiales y mano de obra (descripción, cantidad, precio) asociadas a la reparación.
- Enlazar ese formulario desde la Ficha (por ejemplo dentro de "Editar ficha" o un botón propio en esa sección).
- Verificar que el total de esas líneas se refleje en el desglose de "Cobro" (Materiales, Mano de obra, Total).
**Como comprobar que quedo bien:**
- Se puede agregar, editar y eliminar una línea de material o mano de obra desde la Ficha de reparación y el total se recalcula al instante.
- El desglose de "Cobro" (Materiales, Mano de obra, Total) refleja exactamente lo cargado.

### Sin botón para subir fotos de llegada
**Que pasa hoy:** La Ficha de reparación muestra las "Fotos de llegada" en miniatura y explica que "la foto respalda ante reclamos por rayones", pero el propio documento indica que "en esta pantalla no hay botón para subir fotos".
**Por que importa:** Sin poder subir las fotos, la joyería se queda sin la evidencia visual del estado real de la pieza al llegar, perdiendo el respaldo ante reclamos de la clienta por rayones u otros daños previos.
**Que hacer:**
- Revisar si el formulario "Recibir pieza" permite adjuntar fotos al crear la reparación; si no, es el primer lugar donde falta.
- Agregar un control para subir una o varias fotos de llegada desde la Ficha de reparación (por ejemplo en "Editar ficha" o en la sección "La pieza").
- Reutilizar el componente/almacenamiento de fotos que ya use el módulo de Joyas, definiendo formato y tamaño máximo permitido.
- Mostrar las miniaturas subidas junto con el contador que ya usa "Pieza recibida (fecha y cantidad de fotos)" en la Historia, para que coincidan.
**Como comprobar que quedo bien:**
- Desde la Ficha (o desde Recibir pieza) se puede subir al menos una foto y aparece en miniatura en "Fotos de llegada".
- El contador de fotos de "Pieza recibida" en la Historia coincide con las fotos realmente subidas.

### Faltan botones de avance hacia "No aceptada" y "Cancelada"
**Que pasa hoy:** Los estados "No aceptada" y "Cancelada" existen en el sistema (aparecen en el recuadro "Fuera del tablero" y como opciones de la etiqueta de estado), pero entre los botones de avance descritos (Pendiente→Cotizada→Aprobada→En proceso→Lista→Entregada, más "La clienta no aceptó" en Cotizada) no aparece ninguno que lleve a "Cancelada"; de hecho el propio documento aclara sobre la Ficha de reparación que "no tiene botón para borrar ni cancelar la reparación".
**Por que importa:** Si el taller recibe una pieza que la clienta ya no quiere reparar o que hay que anular por error, no hay forma de moverla a un estado "fuera del tablero" correcto, y la reparación queda atascada en columnas activas o se maneja con datos inconsistentes.
**Que hacer:**
- Revisar en el código a qué estado exacto lleva el botón "La clienta no aceptó" (Cotizada) y confirmar si mapea a "No aceptada" o a otro valor distinto.
- Verificar si existe algún trigger (botón, acción de menú) que lleve a "Cancelada" en cualquier estado, incluyendo Pendiente y Aprobada, aunque el documento indique que no lo hay en la Ficha.
- Si falta, agregar una acción de "Cancelar reparación" disponible desde los estados abiertos (con confirmación, como los demás botones de avance), y asegurar que "La clienta no aceptó" quede correctamente ligado a "No aceptada".
- Actualizar el recuadro "Fuera del tablero" y los contadores del tablero para que reflejen estas transiciones nuevas o corregidas.
**Como comprobar que quedo bien:**
- Desde cualquier estado abierto de una reparación se puede llegar a "Cancelada" mediante un botón visible, con confirmación previa.
- El botón "La clienta no aceptó" deja la reparación visiblemente en estado "No aceptada" dentro de "Fuera del tablero".

### Sin firma de entrega ni impresión del recibo con la garantía
**Que pasa hoy:** La Historia de la Ficha de reparación menciona el paso "Entrega con firma", y la sección de Garantía aclara que esta "sale impresa en el recibo de entrega"; sin embargo, no hay ningún control para capturar la firma de la clienta ni un botón para imprimir ese recibo en ninguna parte de la ficha.
**Por que importa:** Sin firma ni recibo impreso, la joyería no puede acreditar que la clienta recibió conforme la pieza ni entregarle el respaldo escrito de la garantía, debilitando su posición ante un reclamo posterior.
**Que hacer:**
- Revisar qué hace hoy el botón "Entregar a la clienta" (estado Lista → Entregada): confirmar si solo cambia el estado o si ya dispara algo relacionado con firma/recibo que no esté documentado.
- Agregar una captura de firma (dibujo táctil o imagen) como parte del flujo de "Entregar a la clienta", antes de confirmar la entrega.
- Construir la plantilla del recibo de entrega (imprimible/PDF, en la línea de la Nota de venta) que incluya los datos de garantía (duración y vencimiento) y un botón para imprimirlo o descargarlo desde la ficha.
- Guardar la firma capturada y dejar el recibo accesible después de la entrega (por ejemplo, junto al paso "Entrega con firma" en la Historia).
**Como comprobar que quedo bien:**
- Al confirmar "Entregar a la clienta" el sistema exige y guarda una firma antes de completar la entrega.
- Existe un botón para imprimir/descargar el recibo de entrega y ese recibo muestra la garantía (duración y vencimiento).

### Un solo permiso "Reparaciones" para todo, incluido cobrar
**Que pasa hoy:** El módulo Reparaciones usa un único permiso ("Reparaciones") para todo el taller —ver, crear, editar y también cobrar (Registrar pago)—, a diferencia de módulos como Ventas, Pagos o Joyas, que separan Ver, Crear, Editar, Eliminar y permisos extra como "Cobrar saldos pendientes".
**Por que importa:** Cualquier usuario con acceso al taller puede registrar cobros de reparaciones sin que el dueño pueda restringir esa acción por separado, lo que eleva el riesgo de manejo indebido de efectivo y no permite roles acotados (por ejemplo, un técnico que solo diagnostica).
**Que hacer:**
- Revisar el enforcement del permiso "Reparaciones" en backend y frontend para confirmar que hoy un único flag habilita crear, editar y cobrar.
- Definir permisos separados (Ver, Crear, Editar y un extra tipo "Cobrar reparaciones"), siguiendo el patrón ya usado en Pagos ("Cobrar saldos pendientes").
- Actualizar los controles de UI (Recibir pieza, Editar ficha, botones de avance de estado, Registrar pago) para validar el permiso específico correspondiente, no solo "Reparaciones".
- Migrar los roles existentes para que conserven el acceso equivalente tras separar los permisos, sin bloquear a quien ya podía cobrar.
**Como comprobar que quedo bien:**
- Un rol con "Reparaciones - Ver" pero sin el permiso de cobrar puede ver el tablero y la ficha, pero el botón "Registrar pago" queda bloqueado o ausente.
- La tabla de Roles y permisos muestra columnas separadas para Reparaciones igual que en los demás módulos.

### Permiso "Reporte del taller" sin ningún reporte que lo use
**Que pasa hoy:** En Roles y permisos existe el permiso extra "Reporte del taller" dentro del módulo Reparaciones, pero el propio tablero de Reparaciones aclara que "no tiene exportar a Excel/PDF ni imprimir en esta pantalla", y la Ficha de reparación tampoco ofrece esas opciones.
**Por que importa:** Un permiso que no controla ninguna funcionalidad confunde a quien arma roles (cree estar habilitando un reporte inexistente) y deja sin resolver una necesidad real de la joyería: poder exportar o imprimir el desempeño del taller.
**Que hacer:**
- Buscar en el código una ruta, componente o endpoint de "Reporte del taller" ya implementado pero no enlazado desde el menú o el tablero.
- Si no existe, construir el reporte del taller (exportable a Excel/PDF e imprimible) con métricas equivalentes a las tarjetas del tablero (En el taller, Esperando respuesta, Listas sin retirar, Cobrado este mes), filtrable por fecha y técnico, y protegerlo con el permiso "Reporte del taller".
- Si se decide no construirlo por ahora, documentar y retirar el permiso huérfano de Roles y permisos para no confundir a quien configura roles.
**Como comprobar que quedo bien:**
- Con el permiso "Reporte del taller" activo aparece un botón o pantalla de reporte del taller con exportar a Excel/PDF o imprimir.
- Sin ese permiso, el acceso a ese reporte queda bloqueado, igual que el resto de permisos del sistema.

## 5. Resumen, ganancia y gastos

### La Ganancia neta del Resumen y la Ganancia real de la pantalla Ganancia no cuadran entre si

**Que pasa hoy:** La tarjeta "Ganancia neta" del Resumen general se calcula con los gastos restados y "con lo del taller sumado", mientras que la "Ganancia real" de la pantalla Ganancia se calcula solo como ganancia bruta menos gastos, sin ninguna mencion al taller en su formula.

**Por que importa:** La dueña de la joyeria puede ver dos numeros de ganancia distintos para el mismo periodo sin ninguna explicacion visible de la diferencia, lo que le hace desconfiar de los reportes y le dificulta decidir cuanto retirar del negocio o cuanto realmente gano el taller de reparaciones.

**Que hacer:**
- Ubicar en el codigo el calculo de "Ganancia neta" del Resumen y confirmar exactamente que campos del cobro de las reparaciones (Revision, Materiales, Mano de obra, tal como aparecen en la seccion "Cobro" de la Ficha de reparacion) se estan sumando.
- Ubicar el calculo de "Ganancia real" en la pantalla Ganancia y verificar si el taller esta excluido a proposito o por un olvido.
- Definir con el equipo de producto una sola formula de ganancia real (con o sin taller) y aplicarla igual en ambas pantallas, o bien mostrar el aporte del taller como una linea separada y explicita en ambas.
- Si se documenta la diferencia (Resumen incluye taller, Ganancia no), agregar una nota visible en la UI de ambas pantallas que lo aclare, similar a la nota "Ya con los gastos restados".

**Como comprobar que quedo bien:**
- Para el mismo rango de fechas, comparando el Resumen (que siempre suma todos los almacenes, sin filtro de Almacen) con la pantalla Ganancia filtrada por Almacen = "Todos", la Ganancia neta y la Ganancia real coinciden (o la diferencia queda explicada con una nota visible que indica cuanto corresponde al taller).
- Existe un caso de prueba con ventas, gastos y al menos una reparacion de taller cobrada en el periodo que verifica el numero final en ambas pantallas.

### El filtro de Almacen en Ganancia no se aplica a los gastos

**Que pasa hoy:** En la pantalla Ganancia, al filtrar por un Almacen especifico, las ventas mostradas si quedan filtradas por ese almacen, pero los gastos que se restan para calcular la "Ganancia real" son todos los del rango de fechas sin importar el almacen del gasto.

**Por que importa:** Si la joyeria tiene mas de un almacen, la ganancia real que se muestra al filtrar por un almacen especifico queda distorsionada: se le restan gastos de otras tiendas o depositos, mostrando una ganancia menor a la real de ese almacen (o, si el otro almacen no tiene gastos, una ganancia real igual a la global aunque se este mirando un solo almacen). Esto puede llevar a decisiones equivocadas sobre que sucursal es rentable.

**Que hacer:**
- Ubicar en el codigo la consulta que arma la tarjeta "Ganancia real" y la que trae los gastos del periodo, y confirmar que esta ultima no recibe ni aplica el filtro de almacen actualmente seleccionado.
- Modificar la consulta de gastos para que, cuando hay un Almacen elegido (distinto de "Todos"), solo sume los gastos registrados con ese mismo Almacen.
- Revisar el campo Almacen del formulario de Gastos (aparece y es obligatorio solo si hay mas de un almacen; con uno solo se pone automaticamente) para asegurar que todo gasto quede correctamente asociado a un almacen y no queden gastos "sin almacen" que compliquen el filtro.
- Verificar si en los datos actuales existen gastos que deberian aplicar a todos los almacenes (por ejemplo alquiler de oficina central); si los hay, decidir explicitamente con el equipo de producto como se reparten entre almacenes o si quedan fuera del filtro, y dejarlo claro en la nota de la tarjeta ("Ya descontados Bs ... de gastos").

**Como comprobar que quedo bien:**
- Con datos de prueba de dos almacenes con gastos distintos, al filtrar Ganancia por un almacen especifico, la nota "Ya descontados Bs ... de gastos" y la Ganancia real solo reflejan los gastos de ese almacen (verificable sumando manualmente los gastos filtrados en la pantalla Gastos para ese mismo almacen y rango de fechas).
- Al elegir "Todos" en el filtro de Almacen, la Ganancia real sigue sumando los gastos de todos los almacenes como hoy (sin regresion).

### El permiso "Reporte de clientas" no tiene ninguna pantalla asociada

**Que pasa hoy:** En Roles y permisos, el grupo Reportes incluye el permiso "Reporte de clientas" junto a "Reporte de ganancias", pero en todo el documento de contenido del sistema no se describe ninguna pantalla de reporte de clientas (solo existen las pantallas Resumen y Ganancia, y esta ultima permite ver la ganancia agrupada "por Clienta", que es distinto de un reporte de clientas propiamente dicho).

**Por que importa:** Un rol puede tener activado el permiso "Reporte de clientas" sin que exista ninguna funcion real que ese permiso proteja, lo que confunde a quien configura roles (no sabe que esta habilitando) y sugiere que hay una pantalla planeada o eliminada cuyo permiso quedo huerfano en el codigo.

**Que hacer:**
- Buscar en el codigo fuente todas las referencias al permiso "Reporte de clientas" (nombre de permiso, constante o slug asociado) y verificar si controla alguna ruta, componente o endpoint existente.
- Si no protege nada, decidir con el equipo de producto si: (a) se debe construir la pantalla de reporte de clientas que falta, o (b) el permiso debe eliminarse de Roles y permisos por ser un remanente sin uso.
- Si la decision es construir la pantalla, definir su alcance minimo (por ejemplo: ranking de clientas por monto comprado, frecuencia de compra y saldo pendiente) reutilizando los datos ya disponibles en Clientes / Detalle de cliente (Comprado, Pagado, Debe) y en la vista "por Clienta" de la pantalla Ganancia.
- Documentar la decision final para que el permiso y la funcionalidad queden consistentes con lo que el usuario ve en Roles y permisos.

**Como comprobar que quedo bien:**
- El permiso "Reporte de clientas" en Roles y permisos corresponde a una pantalla real y accesible cuando el rol lo tiene activado, o el permiso ya no aparece en la lista si se decidio eliminarlo.
- Un usuario con el permiso activado (y sin "Reporte de ganancias") puede acceder a la funcion de reporte de clientas sin ver el mensaje "No tienes acceso a esta pantalla".

## 6. Tienda en linea (WooCommerce)

### Pedido "Entregado" se marca como pagado sin confirmar el cobro

**Qué pasa hoy:** Cuando WooCommerce marca un pedido como "Entregado", AnnyPos registra la venta como pagada en la caja aunque nadie haya activado el interruptor "Pago" ni haya llegado el comprobante.

**Por qué importa:** La caja puede mostrarse cuadrada con ventas que en realidad la clienta no pagó, inflando los ingresos reportados y ocultando cuentas por cobrar reales.

**Qué hacer:**
- Ubicar el código que procesa el estado del pedido entrante desde WooCommerce (job/listener de sincronización de pedidos) y encontrar dónde el estado "Entregado" dispara el marcado de pago.
- Separar la lógica: el estado de entrega no debe alterar el estado de pago de la venta; usar únicamente el campo de estado de pago que envía WooCommerce (pagado/pendiente/parcial).
- Revisar también el flujo de "Guardar cambios" en la ficha del pedido de AnnyPos para confirmar que no dependa del mismo atajo.
- Agregar prueba automatizada que reproduzca: pedido "Entregado" + pago "Sin pagar" en WooCommerce, y verifique que la venta en AnnyPos quede sin pagar.

**Cómo comprobar que quedó bien:**
- Un pedido con estado "Entregado" y pago "Pendiente" en WooCommerce debe sincronizar en AnnyPos como venta "Sin pagar".
- Un pedido "Esperando pago" + "Entregado" no debe aparecer como cobrado en caja/reportes.

### Stock se descuenta con pedidos web sin pagar y permite negativos

**Qué pasa hoy:** El stock de una joya se descuenta apenas entra un pedido de la web, sin importar si ya está pagado; si no alcanza, el sistema deja el stock en negativo y solo lo anota en el Registro, en vez de bloquear la importación del pedido.

**Por qué importa:** Piezas ya comprometidas por la web pueden aparecer disponibles en el mostrador, o el inventario deja de coincidir con la realidad, provocando ventas dobles o promesas que no se pueden cumplir.

**Qué hacer:**
- Ubicar la rutina de importación de pedidos (webhook/cron de "Pedidos") y el punto donde se descuenta el stock por línea de pedido.
- Definir e implementar una regla de negocio explícita (ej. reservar stock en vez de descontarlo hasta confirmar el pago, o marcar el pedido como "requiere revisión" cuando el descuento daría negativo) en lugar de solo registrar el evento en el Registro.
- Revisar si el modelo de inventario ya distingue "stock reservado" de "stock disponible", o si hay que agregarlo.
- Hacer visible el caso fuera del Registro técnico, por ejemplo con un aviso en Pedidos en línea o en el Resumen.

**Cómo comprobar que quedó bien:**
- Un pedido web con cantidad mayor al stock disponible debe aplicar la regla definida (reserva/bloqueo) y no dejar stock negativo sin aviso visible para la usuaria.
- El caso debe quedar identificable desde la pantalla de Pedidos en línea, no solo en el Registro técnico.

### El stock sincronizado a la web suma todos los almacenes

**Qué pasa hoy:** El stock que se sube a WooCommerce es la suma de existencias de todos los almacenes/depósitos, sin distinguir cuáles realmente despachan pedidos web.

**Por qué importa:** Una clienta puede comprar por la web una pieza que físicamente está en un depósito que no atiende pedidos en línea, generando pedidos que no se pueden preparar ni entregar.

**Qué hacer:**
- Revisar el job de sincronización de "Stock" hacia WooCommerce y el cálculo de cantidad disponible por joya.
- Agregar un concepto de "almacén(es) habilitados para venta web" configurable, y cambiar el cálculo para sumar solo esos almacenes.
- Revisar si la ficha de almacén necesita un campo/interruptor nuevo para marcarlo como "despacha pedidos web".
- Aplicar la misma definición de almacenes web al descuento de stock al importar pedidos (ver hallazgo de stock negativo), para que ambos flujos sean consistentes.

**Cómo comprobar que quedó bien:**
- Una joya con stock solo en un almacén no habilitado para web debe sincronizarse a WooCommerce como agotada (0).
- Una joya con stock repartido entre un almacén web y uno no-web debe mostrar en la web solo la cantidad del almacén habilitado.

### Cambios de una joya ya publicada no se actualizan solos en la web

**Qué pasa hoy:** Si se cambia precio, foto, descripción o marca de una joya ya publicada en la web, ese cambio no sube automáticamente: la tarea nocturna solo sube joyas nuevas y la tarea horaria solo actualiza stock. Sin tocar manualmente "Joyas" en Sincronizar ahora, la web queda desactualizada indefinidamente.

**Por qué importa:** La clienta puede ver en la web un precio, foto o descripción vieja aunque ya se haya corregido en el sistema, generando reclamos, ventas a precio incorrecto o desconfianza en la tienda.

**Qué hacer:**
- Revisar los jobs/comandos programados de sincronización (subida nocturna de joyas nuevas y subida horaria de stock) para confirmar por qué excluyen los cambios de joyas ya publicadas.
- Agregar detección de cambios en la joya (ej. timestamp de última modificación o bandera "pendiente de sincronizar") y hacer que una tarea programada suba también las joyas publicadas que cambiaron desde la última corrida.
- Si subir todo el catálogo cada noche es costoso, limitar la subida automática a las joyas modificadas desde la última sincronización.
- Actualizar el texto de "Sincronización automática" en pantalla para que describa el comportamiento real una vez corregido.

**Cómo comprobar que quedó bien:**
- Cambiar precio o foto de una joya ya publicada y esperar las tareas automáticas (noche y hora); la web debe reflejar el cambio sin usar el botón manual "Joyas".
- La descripción de "Sincronización automática" en pantalla debe coincidir con lo que realmente sincroniza el sistema.

### La traída nocturna de joyas desde la web (3:00) es invisible y sin control

**Qué pasa hoy:** Existe una tarea automática a las 3:00 que trae joyas nuevas desde la web hacia el sistema, pero no aparece en la lista de "Sincronización automática" de la pantalla; el usuario no puede verla ni saber si corrió.

**Por qué importa:** Combinada con la subida de joyas del sistema hacia la web (tarea de las 2:00), crea riesgo de duplicados (una joya creada en el sistema, subida a la web, y luego traída de vuelta como si fuera nueva) o de que un lado le gane al otro, sin que nadie pueda diagnosticarlo.

**Qué hacer:**
- Ubicar en el código el scheduler/cron que ejecuta la tarea de "joyas desde la web" a las 3:00 y confirmar qué crea o modifica en el sistema.
- Agregar esta tarea a la lista visible de "Sincronización automática" en la pantalla de Sincronización, igual que las demás.
- Revisar la lógica de deduplicación entre esta tarea y la subida de joyas nuevas (2:00), usando el ID/SKU de WooCommerce como llave única antes de crear un registro.
- Confirmar si esta tarea ya escribe sus resultados en el Registro; si no lo hace, agregarlo, para poder auditarla igual que las demás sincronizaciones.

**Cómo comprobar que quedó bien:**
- La pantalla de Sincronización debe listar la tarea "Joyas desde la web — 3:00" junto con las demás tareas automáticas.
- Crear una joya en el sistema y subirla a la web poco antes de las 3:00 no debe generar una joya duplicada tras esa corrida.

### Contadores y filtros de Pedidos en línea, Reseñas y Clientas de la web solo ven el lote cargado

**Qué pasa hoy:** Los contadores (tarjetas) y los filtros de las pantallas de Pedidos en línea, Reseñas y Clientas de la web se calculan solo sobre los 30 registros más recientes que se cargan, no sobre el total real en la web.

**Por qué importa:** Un filtro puede mostrar "0 resultados" o un conteo bajo cuando en realidad existen más resultados fuera de ese lote de 30, llevando a la usuaria a concluir erróneamente que algo no existe.

**Qué hacer:**
- Revisar el código de las tres pantallas donde se piden los datos a WooCommerce y donde se aplican filtros y contadores.
- Mover el filtrado (estado, pago, fechas, búsqueda) al lado de la API de WooCommerce en vez de aplicarlo solo sobre el lote ya descargado, para que conteos y resultados reflejen el total real.
- Si mover el filtro al servidor no es viable de inmediato, dejar explícito en la interfaz que el filtro solo aplica al lote cargado (extender a Reseñas y Clientas el aviso tipo "Se muestran {n} de {total}" que ya existe en Pedidos).
- Confirmar si la API de WooCommerce soporta paginación/filtrado remoto para las tres entidades y usarla.

**Cómo comprobar que quedó bien:**
- Con más de 30 pedidos/reseñas/clientas y un filtro cuyo resultado está fuera de las primeras 30, el sistema debe seguir mostrando ese resultado o avisar explícitamente que el filtro es parcial, nunca un "0 resultados" falso.
- Los contadores de las tarjetas deben coincidir con el total real filtrado, no solo con lo cargado en pantalla.

### Eliminar una reseña no pide confirmación

**Qué pasa hoy:** El botón "Eliminar" de una reseña la manda directo a la papelera de la web sin ninguna ventana de confirmación, a diferencia de casi todas las demás eliminaciones del sistema.

**Por qué importa:** Un clic accidental borra una reseña real de una clienta (incluida una de compra verificada) sin posibilidad de revertirlo desde la interfaz, rompiendo la consistencia de UX del resto del sistema, donde eliminar siempre pide confirmar.

**Qué hacer:**
- Ubicar el componente/handler del botón "Eliminar" en la pantalla de Reseñas.
- Agregar el mismo patrón de diálogo de confirmación que usan las demás eliminaciones del sistema (ej. el de "Eliminar usuario" o "Vaciar registro"), aclarando que la reseña se manda a la papelera de la web.
- Confirmar si WooCommerce permite restaurar desde la papelera y, de ser así, mencionarlo en el texto de confirmación.

**Cómo comprobar que quedó bien:**
- Al tocar "Eliminar" en una reseña debe aparecer un diálogo pidiendo confirmar antes de mandarla a la papelera; cancelar debe dejar la reseña intacta.

## 7. Administracion y ajustes

### Botones Editar/Eliminar visibles sin permiso en Lista de ventas

**Qué pasa hoy:** En la Lista de ventas los botones "Editar" y "Eliminar" se muestran siempre a cualquier usuario, sin importar su rol, tanto en el menú de opciones de cada fila como en la ventana de detalle de la venta; el documento aclara que "el permiso lo aplica el servidor", es decir que hoy solo el backend rechaza la acción si el rol no la tiene.

**Por qué importa:** Una vendedora sin permiso de editar o eliminar ventas ve y puede pulsar botones que no le corresponden, y solo al intentar la acción el servidor se lo rechaza, en vez de que la interfaz refleje desde un principio lo que su rol realmente puede hacer.

**Qué hacer:**
- Ubicar el componente de Lista de ventas y los dos puntos donde se renderizan "Editar" y "Eliminar": el menú de tres puntos de cada fila ("Ver detalle", "Nota de venta", "Editar", "Eliminar") y los botones de la ventana de detalle "Venta N° …".
- Revisar cómo el frontend obtiene los permisos del usuario autenticado (Ventas › Editar, Ventas › Eliminar) y usarlos para condicionar el render de cada botón en ambos lugares.
- Ocultar (no solo deshabilitar) "Editar" si el rol no tiene Ventas › Editar, y "Eliminar" si no tiene Ventas › Eliminar.
- Combinar esta nueva condición de permiso con la regla ya existente que bloquea Editar/Eliminar cuando la venta tiene una devolución registrada, de modo que ambas reglas se apliquen juntas sin que una anule el efecto de la otra.
- Conservar la validación del servidor como respaldo (defensa en profundidad); no reemplazarla por la del cliente.

**Cómo comprobar que quedó bien:**
- Con un rol sin permiso de Editar/Eliminar en Ventas, ni la fila de la Lista de ventas ni la ventana de detalle de una venta muestran esos botones.
- Con un rol que sí tiene esos permisos, los botones siguen apareciendo y funcionando igual que antes, incluida la regla de bloqueo cuando la venta tiene una devolución registrada.

### Menú completo visible antes de cargar los permisos del usuario

**Qué pasa hoy:** Mientras el sistema todavía no sabe los permisos de quien acaba de iniciar sesión, muestra el menú completo por un instante; el servidor sigue protegiendo los datos, pero se alcanza a ver brevemente una opción a la que no se tiene acceso.

**Por qué importa:** Aunque no hay fuga de datos, la usuaria ve por un momento opciones que su rol no debería mostrarle (por ejemplo Ganancia o Usuarios), lo que genera confusión y da la impresión de que el sistema no respeta los permisos.

**Qué hacer:**
- Ubicar dónde se arma el menú lateral/inferior a partir de los permisos del usuario y dónde se dispara la carga de esos permisos tras el login.
- Mientras los permisos aún no llegan, mostrar un estado de carga (menú vacío o esqueleto) en lugar del menú completo.
- Renderizar las opciones reales del menú solo después de que la respuesta de permisos haya llegado.

**Cómo comprobar que quedó bien:**
- Al iniciar sesión con un rol limitado (por ejemplo solo Punto de venta), en ningún momento se alcanza a ver una opción de menú que ese rol no tiene.
- Simulando una red lenta (throttling) o retrasando artificialmente la respuesta de permisos, confirmar que durante la espera se ve el estado de carga y no el menú completo, y que en cuanto llegan los permisos el menú se actualiza a las opciones correctas.
- El tiempo hasta que aparece el menú definitivo no aumenta de forma perceptible para la usuaria en una red normal.

### Permiso único "Ver" habilita crear, editar y eliminar en cuatro módulos

**Qué pasa hoy:** En Roles y permisos, los módulos Almacenes, Tienda en línea, Idiomas y Configuración solo ofrecen la acción "Ver", pero ese único permiso también deja crear, editar y eliminar dentro de esas pantallas (por ejemplo, crear/editar/eliminar almacenes, o agregar/editar/eliminar idiomas), a diferencia de módulos como Ventas, Joyas, Inventario, Gastos, Clientes, Proveedores, Usuarios y Roles y permisos, que sí separan Ver, Crear, Editar y Eliminar.

**Por qué importa:** La dueña cree que al dar solo "Ver" está limitando a una empleada a consultar, pero esa persona puede en realidad crear o borrar almacenes, cambiar la configuración de la joyería o modificar idiomas/textos del sistema sin que el rol configurado lo refleje.

**Qué hacer:**
- Revisar el backend de Almacenes, Tienda en línea, Idiomas y Configuración para identificar qué endpoints de crear/editar/eliminar hoy solo validan el permiso "Ver" en vez de un permiso propio por acción.
- Agregar los permisos Crear, Editar y Eliminar para estos cuatro módulos en el modelo de Roles y permisos, igual que en los demás módulos que ya los separan.
- Actualizar la tabla de Roles y permisos en la interfaz para mostrar las columnas nuevas en estos módulos.
- Definir la migración de roles existentes (por ejemplo, traducir el "Ver" actual en Ver+Crear+Editar+Eliminar) para no quitarle funciones a nadie sin aviso.

**Cómo comprobar que quedó bien:**
- Un rol con solo "Ver" en Almacenes, Tienda en línea, Idiomas o Configuración puede consultar la pantalla, pero no puede crear, editar ni eliminar (ni ve esos botones).
- Un rol con "Ver" más "Crear"/"Editar"/"Eliminar" marcados en esos módulos sí puede realizar esas acciones, igual que en los módulos que ya separaban permisos.

### Mensaje de "sin acceso" no confirmado para todas las pantallas protegidas

**Qué pasa hoy:** El mensaje "No tienes acceso a esta pantalla" solo está documentado para 7 pantallas (Tienda en línea, Idiomas, Gastos, Reparaciones, Ganancia, Usuarios y Roles y permisos); no queda claro qué ocurre si alguien sin permiso entra directamente a otras pantallas protegidas, como Clientes o Proveedores.

**Por qué importa:** Si esas otras pantallas no muestran el mismo aviso, una usuaria sin permiso podría ver una pantalla en blanco, un error técnico o un comportamiento distinto al escribir la URL a mano, en vez de una explicación clara de por qué no puede entrar.

**Qué hacer:**
- Listar todas las pantallas protegidas por permiso (incluidas Clientes, Proveedores y cualquier otra no mencionada en la documentación) y ubicar en el código el guard de ruta que controla el acceso directo por URL.
- Confirmar que cada pantalla protegida use el mismo componente/mensaje "No tienes acceso a esta pantalla" – "Pídele a la dueña que te habilite este permiso en Roles y permisos.", en vez de manejar el caso de forma distinta o no manejarlo.
- Donde falte el guard (por ejemplo Clientes o Proveedores), agregarlo siguiendo el mismo patrón que las 7 pantallas ya documentadas.

**Cómo comprobar que quedó bien:**
- Entrando por URL directa sin el permiso correspondiente a Clientes, Proveedores y cualquier otra pantalla protegida, todas muestran el mismo mensaje "No tienes acceso a esta pantalla".
- No queda ninguna pantalla protegida por permiso que, al accederse sin permiso por URL directa, quede en blanco o lance un error sin mensaje.

## 8. Detalles menores y limpieza de plantilla

### Restos de plantilla genérica sin adaptar (idioma Indonesia y registro en inglés)

**Qué pasa hoy:** El selector de idiomas (Ajustes > Idiomas) trae de fábrica "Español", "English" e "Indonesia" sin relación con el negocio boliviano, y en Tienda en línea > Conexión y sincronización, pestaña "Registro", cada anotación de sincronización muestra su nivel (error, warning, info, success) escrito en inglés en vez de en español.

**Por qué importa:** Son señales visibles de plantilla sin terminar de adaptar: confunden a la dueña o al equipo de la joyería, que ve un idioma que nunca va a usar y palabras en inglés en una pantalla pensada para explicarles en español qué pasó con su sincronización con la web.

**Qué hacer:**
- Ubicar de dónde sale la lista de idiomas de fábrica (Español, English, Indonesia) — normalmente un seed/fixture que corre en la instalación — y quitar ahí la entrada de "Indonesia", o reemplazarla por un idioma que sí tenga sentido para el negocio.
- Mientras tanto, en instalaciones que ya están corriendo, usar el menú de tres puntos de la tarjeta "Indonesia" en Ajustes > Idiomas para "Desactivar" o "Eliminar" esa opción sin tocar Español ni English.
- Ubicar el componente/lógica que arma cada anotación del Registro de sincronización (Tienda en línea > Conexión y sincronización > pestaña "Registro") y encontrar dónde se interpola el nivel (error/warning/info/success).
- Mapear esos cuatro niveles a sus equivalentes en español (p. ej. error, advertencia, información, éxito), conservando el mismo color por nivel (rojo, amarillo, gris, verde).
- Revisar si el nombre técnico de la acción (p. ej. subida de joyas, traída de pedidos) también necesita pasarse a español en el mismo lugar.

**Cómo comprobar que quedó bien:**
- Ajustes > Idiomas ya no ofrece "Indonesia", y al tocar "Usar este idioma" en Español o English el sistema sigue cambiando al instante, sin recargar la página.
- Al provocar al menos un evento de cada tipo (por ejemplo con "Sincronizar ahora"), el Registro de sincronización (pestaña "Registro") muestra los cuatro niveles en español, cada uno con su color correspondiente.

### Botón "Excel" en Lista de ventas descarga un CSV, no un .xlsx

**Qué pasa hoy:** En Lista de ventas, el botón etiquetado "Excel" descarga un archivo ventas-fecha.csv (con acentos correctos), no un archivo .xlsx nativo de Excel.

**Por qué importa:** Quien pulsa "Excel" espera un libro de Excel real; al abrirlo puede toparse con columnas o acentos mal interpretados según la configuración regional de su Excel, y va a pensar que el sistema falló en vez de que el archivo es simplemente un CSV.

**Qué hacer:**
- Ubicar el handler del botón "Excel" en Lista de ventas y confirmar cómo genera el archivo hoy (CSV armado a mano vs. librería de hojas de cálculo).
- Decidir con negocio entre (a) renombrar el botón y el archivo a algo honesto como "CSV"/"Exportar CSV", o (b) cambiar la generación para producir un .xlsx real.
- Si se opta por .xlsx real, revisar que las columnas (las mismas que el reporte en PDF: Fecha, Nota, Cliente, Almacén, Vendedora, Estado, Total, Pagado, Debe, Método, Pago) y los acentos se conserven correctos al abrir en Excel.
- Actualizar de forma consistente el texto del botón y el nombre del archivo descargado según la decisión tomada.

**Cómo comprobar que quedó bien:**
- El nombre del botón coincide con el tipo real de archivo que descarga (o el archivo es un .xlsx válido, si se cambió la generación).
- El archivo descargado abre en Excel/LibreOffice con columnas y acentos correctos, sin avisos de formato.

### La caja rápida (Vender) no tiene impuesto, a diferencia de "Añadir venta"

**Qué pasa hoy:** "Añadir venta" tiene el campo "Impuesto de orden (%)" aplicado al total, mientras que la caja rápida "Vender" solo maneja Subtotal, Descuento y Total (entre el panel "Venta actual" y la ventana "Cobrar venta"), sin ningún campo ni cálculo de impuesto.

**Por qué importa:** Dos flujos de venta del mismo negocio terminan con reglas de impuesto distintas: una venta por mostrador (Vender) nunca cobra impuesto y una venta por "Añadir venta" sí puede llevarlo, lo que produce notas de venta inconsistentes entre sí y puede complicar la parte tributaria de la joyería.

**Qué hacer:**
- Confirmar con negocio si la joyería boliviana debe aplicar el mismo impuesto (o ninguno) en ambos flujos, y dejar la regla esperada por escrito.
- Ubicar el cálculo de totales en Vender (ventana "Cobrar venta" / panel "Venta actual") y en Añadir venta, y verificar si comparten o no la misma lógica.
- Revisar el generador de la nota de venta/ticket/PDF: ya imprime una línea de impuesto "si se activó en configuración" (la misma lógica que usa Añadir venta); confirmar si esa parte del ticket sirve tal cual para Vender o hay que adaptarla.
- Si la regla exige impuesto también en Vender, añadir el campo "Impuesto de orden (%)" a ese flujo, replicando su cálculo y su reflejo en el ticket/nota de venta.
- Si Vender no debe llevar impuesto nunca, dejar esa decisión documentada en el código para que no se "corrija" por error más adelante.

**Cómo comprobar que quedó bien:**
- Una venta con las mismas joyas y precios recibe el mismo trato de impuesto (aplicado o no, con el mismo %) sin importar si se hizo por Vender o por Añadir venta, según la regla confirmada.
- El ticket/nota de venta y el reporte de ventas reflejan correctamente el impuesto cobrado (o su ausencia) en cada flujo, incluida la línea de impuesto del PDF que hoy depende de "si se activó en configuración".

### Falta interruptor para apagar Taller/Reparaciones

**Qué pasa hoy:** En Configuración > Funciones hay interruptores para Tienda en línea, Portal de clientas, Proveedores, Ficha de joyería, Añadir venta y Ajustes de stock, pero ninguno para el módulo de Taller/Reparaciones.

**Por qué importa:** Una joyería que no ofrece reparaciones no puede ocultar esa pantalla (Taller > Reparaciones) ni sus permisos asociados, así que le queda una sección y opciones sin uso que pueden confundir a su equipo o exponer un permiso que no tiene sentido asignar.

**Qué hacer:**
- Ubicar la lista de interruptores de Configuración > Funciones y el modelo/tabla donde se guarda el estado de cada función existente (Tienda en línea, Portal de clientas, Proveedores, Ficha de joyería, Añadir venta, Ajustes de stock).
- Añadir una función "Taller/Reparaciones" siguiendo ese mismo patrón de guardado; al apagarla, ocultar la entrada "Reparaciones" del grupo TALLER en el menú lateral, igual que ya pasa con las demás funciones opcionales al apagarse.
- Decidir si, al apagarla, conviene también ocultar o inhabilitar en Roles y permisos el módulo "Reparaciones" (permiso "Ver" y el extra "Reporte del taller"), para no dejar un permiso asignable sin pantalla asociada.
- Verificar que apagarla no borre reparaciones ya registradas, igual que ya ocurre con las demás funciones opcionales ("lo apagado desaparece del menú sin borrar nada, y al encenderlo vuelve como estaba").
- Revisar otros puntos que dependen de datos del taller aunque la función esté apagada: la propia pantalla del tablero de Taller ya queda cubierta al ocultar su entrada de menú (con eso se ocultan también sus tarjetas "En el taller" y "Cobrado este mes"), pero la tarjeta "Ganancia neta" de Resumen hoy suma siempre "lo del taller"; definir si debe seguir sumándolo o excluirlo mientras el módulo está apagado, y documentar la decisión.

**Cómo comprobar que quedó bien:**
- Apagar "Taller/Reparaciones" en Configuración > Funciones oculta el menú y la pantalla del tablero de Taller (con sus tarjetas y fichas de reparación), y el permiso "Reparaciones"/"Reporte del taller" deja de poder asignarse en Roles y permisos, sin perder los datos ya registrados.
- La tarjeta "Ganancia neta" de Resumen se comporta según la regla definida (sigue sumando el taller o lo excluye) mientras el módulo está apagado.
- Volver a encenderla restaura el menú, el tablero, el permiso y el comportamiento de "Ganancia neta" exactamente como estaban antes.

## Nota de cierre

Este orden es un punto de partida para priorizar el trabajo, no un diagnóstico cerrado: antes de tratar cualquiera de estos puntos como un bug confirmado, hay que verificarlo contra el código real (o con quien conozca el estado actual del sistema), porque el comportamiento pudo haber cambiado desde que se documentó, puede existir una implementación parcial no visible en la interfaz, o el hallazgo puede basarse en una lectura de la documentación que ya no corresponda a lo que hace hoy el sistema.

---

_Este documento fue redactado y verificado con asistencia de IA (Claude), a partir del PDF "AnnyPos - Contenido del sistema de ventas" del 24 de septiembre de 2026, sin acceso al codigo fuente real de AnnyPos. Cada hallazgo debe confirmarse contra el codigo antes de tratarse como un bug cerrado._
