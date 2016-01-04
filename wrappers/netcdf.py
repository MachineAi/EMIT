
import stdlib
import netCDF4
import wrappers
from wrappers import base
from utilities import geometry
from dateutil import parser
import datetime
import numpy

# http://www.hydro.washington.edu/~jhamman/hydro-logic/blog/2013/10/12/plot-netcdf-data/

class Wrapper(base.BaseWrapper):
    """
    Wrapper for NetCDF data types.  Requires user specified inputs that cannot be extracted from NetCDF files in
    a generalized manner:

    tdim -> time variable name
    tunit -> time unit name (datetime.timedelta hours, minutes, seconds, days, etc...)
    starttime -> start time
    xdim -> x location variable name
    ydim -> y location variable name

    """


    def __init__(self, args):
        super(Wrapper, self).__init__()

        handle = netCDF4.Dataset(args['ncpath'], 'r')

        variables = handle.variables.keys()

        tdim = args['tdim']
        xdim = args['xdim']
        ydim = args['ydim']
        tunit = {args['tunit']: 1}
        if isinstance(args['starttime'], datetime.datetime):
            st = args['starttime']
        else:
            st = parser.parse(args['starttime'])

        # make sure the variables provided exist in the nc file
        assert tdim in variables, 'time variable name not specified.  Cannot continue'
        assert xdim in variables, 'x dimension variable name not specified.  Cannot continue'
        assert ydim in variables, 'y dimension variable name not specified.  Cannot continue'



        # get data for these variables
        timesteps = handle.variables[tdim][:]
        times = []
        for ts in timesteps:
            # update the time unit value
            tunit[args['tunit']] = ts

            # unpack the tunit dictionary to create a timedelta object
            dt = datetime.timedelta(**tunit)

            times.append(st + dt)

        variables.remove(tdim)

        x = handle.variables[xdim][:]
        variables.remove(xdim)

        y = handle.variables[ydim][:]
        variables.remove(ydim)

        # create flattened lists of x,y coords from meshgrid
        xcoords, ycoords = numpy.meshgrid(x, y)
        xcoords = xcoords.flatten()
        ycoords = ycoords.flatten()


        # loop through the remaining variables and expose them as outputs
        # for var in variables:
        for v in range(len(variables)):

            var = variables[v]

            # create a unit
            unit = stdlib.Unit()

            unit.UnitName(handle.variables[var].units if 'units' in dir(handle.variables[var]) else 'N/A')
            unit.UnitTypeCV("N/A")
            unit.UnitAbbreviation("N/A")

            # create a variable
            variable = stdlib.Variable()
            variable.VariableNameCV(handle.variables[var].name)
            variable.VariableDefinition("N/A")

            # create geometries
            geoms = geometry.build_point_geometries(xcoords, ycoords)

            # create exchange item
            oei = stdlib.ExchangeItem(name=variable.VariableNameCV(),
                                desc = 'Autogenerated variable parsed from %s'%args['ncpath'],
                                geometry = geoms ,
                                unit = unit,
                                variable = variable,
                                type = stdlib.ExchangeItemType.OUTPUT)

            # flatten each timestep of the data
            values = [v.flatten() for v in handle.variables[var][:]]

            # set these data.  Skip occurrences with mismatched values and times arrays
            if len(values) == len(times):
                success = oei.setValues2(values, times)

                # only expose the exchange item if data was set properly
                if success:
                    # save the oei
                    self.outputs(oei)

        # set metadata
        name = args['ncpath'].split('/')[-1]
        self.name(name)
        self.description('NetCDF data component, '+name)
        self.simulation_start(times[0])
        self.simulation_end(times[-1])
        self.status(stdlib.Status.READY)


    def prepare(self):
        self.status(stdlib.Status.READY)

    def type(self):
        return wrappers.Types.NETCDF

    def run(self,inputs):
        self.status(stdlib.Status.FINISHED)

    def finish(self):
        self.status(stdlib.Status.FINISHED)


