"""
Outputs a set of data profiles along either the X or Z axis
#
Written By: Matthew Stadelman
Date Written: 2016/03/07
Last Modifed: 2016/03/22
#
"""
from ApertureMapModelTools.__core__ import ArgProcessor, get_data_vect
from .__BaseProcessor__ import BaseProcessor


class Profile(BaseProcessor):

    def __init__(self, field, **kwargs):
        super().__init__(field, **kwargs)
        self.output_key = 'profile'
        self.action = 'profile'
        self.arg_processors = {
            'locs': ArgProcessor('locs',
                                 map_func=lambda x: float(x),
                                 min_num_vals=1, out_type='list',
                                 expected='##1, ##2, ##3, ..., ##n',
                                 err_desc_str='to have 1 -> n numeric values'),
            'dir': ArgProcessor('dir',
                                map_func=lambda x: x,
                                min_num_vals=1,
                                out_type='single',
                                expected='str',
                                err_desc_str='val is either x or z')
        }

    def process_data(self, **kwargs):
        r"""
        Takes a list of percentiles specified in **kwargs and generates
        the corresponding set of values.
        """
        #
        self.processed_data = dict()
        dir_ = self.args['dir']
        locs = self.args['locs']
        locs.sort()
        #
        if (dir_.lower() == 'x'):
            # first row is bottom of fracture
            start_ids = [(int(l/100.0*self.nz)+1) for l in locs]
        elif (dir_.lower() == 'z'):
            # first column is left side of fracture
            start_ids = [(int(l/100.0*self.nx)+1) for l in locs]
        else:
            msg = 'Error - Invalid direction: "{}" supplied. '
            msg += 'valid values are x or z.'
            print(msg.format(dir_))
            self.processed_data = None
            return
        #
        fmt = '{:4.2f}'
        self.loc_ids = {fmt.format(loc): sid for loc, sid in zip(locs, start_ids)}
        for loc, st_id in self.loc_ids.items():
            self.processed_data[loc] = get_data_vect(self.data_map, dir_, st_id)

    def output_data(self, filename=None, delim=',', **kwargs):
        r"""
        Creates the output content for data profiles
        """
        #
        if filename is None:
            filename = self.infile
        #
        # getting index before the extension
        ldot = filename.rfind('.')
        #
        # naming ouput file
        dir_ = self.args['dir'].upper()
        name = filename[:ldot]+'-profiles-'+dir_+'-axis'+filename[ldot:]
        self.outfile_name = name
        #
        # outputting data
        content = dir_+'-axis profile data from file: '+self.infile+'\n'
        fmt = 'Location: {0}%{1}Row Number: {2}\n'
        for loc in self.loc_ids:
            content += fmt.format(loc, delim, self.loc_ids[loc])
            content += delim.join(map(str, self.processed_data[loc]))+'\n'
        content += '\n'
        #
        self.outfile_content = content
